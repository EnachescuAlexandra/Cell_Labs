// @vitest-environment jsdom
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {cleanup, fireEvent, render, screen, waitFor, within} from '@testing-library/react';
import {App} from './App';
import type {Config} from './api';
const config:Config={automaton:{name:'Game of Life',width:2,height:1,states:['DEAD','ALIVE'],neighborhood:'moore',default:'keep',rules:[]},initial_state:[['DEAD','ALIVE']],experiment:{generations:1,retain_history:false,save_result:false}};
beforeEach(()=>{vi.stubGlobal('fetch',vi.fn(async(url:string,options?:RequestInit)=>{
 const body=options?.body?JSON.parse(String(options.body)):null;
 const data=url==='/api/health'?{status:'ok'}:url==='/api/automata'?[{...config.automaton,id:'game_of_life'},{...config.automaton,id:'crystal_growth',name:'Crystal Growth'}]:url.includes('/api/automata/')?{...config,automaton:{...config.automaton,name:url.endsWith('crystal_growth')?'Crystal Growth':'Game of Life'}}:url.includes('/simulations/')?{...body,final_state:[['ALIVE','DEAD']],history:body.experiment.retain_history?[body.initial_state,[['ALIVE','DEAD']]]:null}:{};
 return {ok:true,json:async()=>data};
}));});
afterEach(()=>{cleanup();vi.unstubAllGlobals();});
describe('dashboard controls',()=>{
 it('renders configuration rules, AND conditions, unconditional transitions, and the default for built-in and uploaded definitions',async()=>{
  const {container}=render(<App/>);await screen.findByRole('img');
  const builtin:Config={...config,automaton:{...config.automaton,rules:[
   {from:'DEAD',to:'ALIVE',conditions:[{state:'ALIVE',operator:'==',value:1},{state:'DEAD',operator:'<=',value:0}]},
   {from:'ALIVE',to:'DEAD',conditions:[]},
  ]}};
  vi.mocked(fetch).mockResolvedValueOnce({ok:true,json:async()=>builtin} as Response);
  fireEvent.change(screen.getByLabelText('Automaton'),{target:{value:'game_of_life'}});
  await waitFor(()=>expect(container.querySelector('.transition-rules')?.textContent).toContain('DEAD → ALIVE'));
  const section=container.querySelector('details.transition-rules') as HTMLDetailsElement;
  expect(section.open).toBe(false);
  fireEvent.click(within(section).getByText('Transition rules'));
  expect(section.open).toBe(true);
  expect(within(section).getAllByRole('listitem')).toHaveLength(2);
  expect(within(section).getByText('Count of ALIVE neighbors == 1 AND Count of DEAD neighbors <= 0')).toBeTruthy();
  expect(within(section).getByText('ALIVE → DEAD')).toBeTruthy();
  expect(within(section).getByText('Unconditional (for this source state).')).toBeTruthy();
  expect(within(section).getByText('Default (keep): keep the current state when no rule matches.')).toBeTruthy();
  const uploaded:Config={...config,automaton:{...config.automaton,name:'Uploaded system',rules:[
   {from:'ALIVE',to:'DEAD',conditions:[{state:'DEAD',operator:'!=',value:1}]},
  ]}};
  vi.mocked(fetch).mockResolvedValueOnce({ok:true,json:async()=>uploaded} as Response);
  const file=new File([JSON.stringify(uploaded)],'custom.json',{type:'application/json'});
  Object.defineProperty(file,'text',{value:async()=>JSON.stringify(uploaded)});
  fireEvent.change(container.querySelector('input[type="file"]')!,{target:{files:[file]}});
  await screen.findByRole('img',{name:/Uploaded system/});
  expect(within(section).getAllByRole('listitem')).toHaveLength(1);
  expect(within(section).getByText('Count of DEAD neighbors != 1')).toBeTruthy();
  expect(within(section).queryByText('DEAD → ALIVE')).toBeNull();
  expect(within(section).getByText('Default (keep): keep the current state when no rule matches.')).toBeTruthy();
  fireEvent.click(within(section).getByText('Transition rules'));
  expect(section.open).toBe(false);
 });
 it('loads, steps using the API, navigates real history, and resets',async()=>{
  render(<App/>);await screen.findByRole('img',{name:/generation 0/});
  fireEvent.click(screen.getByLabelText('Retain generation history'));
  fireEvent.click(screen.getByRole('button',{name:'Next generation →'}));
  await screen.findByRole('img',{name:/generation 1/});
  fireEvent.click(screen.getByRole('button',{name:'← Previous'}));
  await screen.findByRole('img',{name:/generation 0/});
  fireEvent.click(screen.getByRole('button',{name:'Next generation →'}));
  fireEvent.click(screen.getByRole('button',{name:'↺ Reset'}));
  await screen.findByRole('img',{name:/generation 0/});
 });
 it('plays, pauses, and stops when switching systems',async()=>{
  render(<App/>);await screen.findByRole('img');
  fireEvent.change(screen.getByLabelText('Playback interval'),{target:{value:'250'}});
  fireEvent.click(screen.getByRole('button',{name:'▶ Play'}));
  await screen.findByRole('img',{name:/generation 1/});
  fireEvent.click(screen.getByRole('button',{name:'Ⅱ Pause'}));
  fireEvent.click(screen.getByRole('button',{name:'▶ Play'}));
  fireEvent.change(screen.getByLabelText('Automaton'),{target:{value:'crystal_growth'}});
  await screen.findByRole('img',{name:/Crystal Growth, generation 0/});
  expect(screen.getByRole('button',{name:'▶ Play'})).toBeTruthy();
 });
 it('shows backend validation failures and releases the loading state',async()=>{
  render(<App/>);await screen.findByRole('img');
  vi.mocked(fetch).mockResolvedValueOnce({ok:false,json:async()=>({error:{message:'Invalid configuration.'}})} as Response);
  fireEvent.click(screen.getByRole('button',{name:'Next generation →'}));
  await screen.findByRole('alert');
  await waitFor(()=>expect((screen.getByRole('button',{name:'Next generation →'}) as HTMLButtonElement).disabled).toBe(false));
 });
 it('rejects a late simulation result after Reset and prevents overlapping runs',async()=>{
  render(<App/>);await screen.findByRole('img');
  let finish!:(value:Response)=>void;
  vi.mocked(fetch).mockImplementationOnce(()=>new Promise<Response>(resolve=>{finish=resolve;}));
  const before=vi.mocked(fetch).mock.calls.length;
  fireEvent.click(screen.getByRole('button',{name:'Next generation →'}));
  expect((screen.getByRole('button',{name:'Next generation →'}) as HTMLButtonElement).disabled).toBe(true);
  fireEvent.click(screen.getByRole('button',{name:'Next generation →'}));
  expect(vi.mocked(fetch).mock.calls.length).toBe(before+1);
  fireEvent.click(screen.getByRole('button',{name:'↺ Reset'}));
  finish({ok:true,json:async()=>({...config,final_state:[['ALIVE','DEAD']],history:null})} as Response);
  await waitFor(()=>expect((screen.getByRole('button',{name:'Next generation →'}) as HTMLButtonElement).disabled).toBe(false));
  expect(screen.getByRole('img',{name:/generation 0/})).toBeTruthy();
 });
});
