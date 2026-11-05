export type Grid = string[][];
export type TransitionRule = {from:string; to:string; conditions:{state:string; operator:'=='|'!='|'<'|'<='|'>'|'>='; value:number}[]};
export type Definition = {name:string; width:number; height:number; states:string[]; neighborhood:string; default:'keep'; rules:TransitionRule[]};
export type Config = {automaton:Definition; initial_state:Grid; experiment:{generations:number; retain_history:boolean; save_result:boolean}};
export type Result = Config & {final_state:Grid; history:Grid[]|null};
export async function api<T>(path:string, body?:unknown):Promise<T> {
  const response = await fetch('/api'+path, body === undefined ? undefined : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const data = await response.json();
  if(!response.ok) throw new Error([data.error?.message ?? 'Request failed.', ...(data.error?.details ?? []).map((e:{field:string;message:string})=>`${e.field}: ${e.message}`)].join(' '));
  return data;
}
