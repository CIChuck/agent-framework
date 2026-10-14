import copy,importlib.util,json
from pathlib import Path
root=Path('/private/tmp/friday-mcp-upgrade/work')
spec=importlib.util.spec_from_file_location('independent_board',root/'scripts/friday-dev-board.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=m.load_board(root);active='docs/planning/active/friday-mcp-protocol-upgrade/';review='docs/planning/review/friday-mcp-protocol-upgrade/'
current=m._current_packet_paths(root)
actual=m.validate_board(b,root)
assert not actual and active in current
completed=copy.deepcopy(b);task=next(t for t in completed['tasks'] if t['id']=='friday-mcp-protocol-upgrade');task['work_state']='completed';task['validation'].append('independent synthetic VERIFIED placeholder; no actual transition authorized')
keep_errors=m.validate_board(completed,root)
task['packet']=review
original=m._current_packet_paths;m._current_packet_paths=lambda r:original(r)|{review}
review_errors=m.validate_board(completed,root)
registered={t['packet'] for t in completed['tasks'] if t['packet'].startswith('docs/planning/')}
orphans=sorted((current|{review})-registered)
print(json.dumps({'probe':'in-memory only, original checker logic; no candidate writes or board transition','current_board_errors':actual,'active_frozen_packet_in_actual_inventory':active in current,'completed_retaining_active_packet_errors':keep_errors,'completed_with_review_index_errors':review_errors,'hypothetical_inventory_minus_board':orphans,'expected_completed_prefix':m._expected_packet_prefix(task),'review_packet_absence_is_simulation_artifact':'packet does not exist error is expected because probe does not write hypothetical review README; orphan active error persists even if review is created'},indent=2))
assert any('packet must be under docs/planning/review/' in x for x in keep_errors)
assert 'current planning packet is absent from board: '+active in review_errors
