import importlib.util,json,sys
from pathlib import Path
from pydantic import BaseModel,ValidationError
out=Path('/private/tmp/telem-01/REM-004/approved-execution/remediator')
class Parent(BaseModel):
 value:str
class Child(Parent):
 extra:int
models={}
for variant in ['original','converted']:
 path=out/'variance-matrix-source/MoltbookResponse'/f'{variant}.py'
 name=f'rem004_pydantic_{variant}'
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
 parent_model=module.MoltbookResponse[Parent]
 child_model=module.MoltbookResponse[Child]
 good_parent=parent_model.model_validate({'success':True,'data':{'value':'synthetic'}})
 good_child=child_model.model_validate({'success':True,'data':{'value':'synthetic','extra':1}})
 rejected=False
 try: child_model.model_validate({'success':True,'data':{'value':'synthetic'}})
 except ValidationError:rejected=True
 models[variant]={'parent_schema':parent_model.model_json_schema(),'child_schema':child_model.model_json_schema(),'parent_dump':good_parent.model_dump(),'child_dump':good_child.model_dump(),'missing_child_field_rejected':rejected,'public_subscriptability':parent_model.__name__=='MoltbookResponse[Parent]'}
result={'variants':models,'schema_dump_contract_equal':models['original']==models['converted']}
print(json.dumps(result,sort_keys=True))
(out/'pydantic-generic-raw.json').write_text(json.dumps(result,indent=2)+'\n')
