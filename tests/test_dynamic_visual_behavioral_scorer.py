"""Retained V1-V5c shapes; original session IDs are recorded in the evaluation ledger."""
from __future__ import annotations
import contextlib, importlib.util, io, json, shutil, subprocess, tempfile, threading, unittest, uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCORER_PATH = ROOT / "tests" / "behavioral" / "score_dynamic_visual_reference.py"

def load_scorer():
    spec = importlib.util.spec_from_file_location("dvc_scorer", SCORER_PATH)
    module = importlib.util.module_from_spec(spec); assert spec.loader
    spec.loader.exec_module(module); return module

class DynamicVisualBehavioralScorerTests(unittest.TestCase):
    def setUp(self): self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup); self.dir=Path(self.temp.name); self.skill=self.dir/'isolated'/'godot-game-production'; (self.skill/'scripts').mkdir(parents=True); shutil.copy2(ROOT/'godot-game-production'/'scripts'/'visual_contract.py',self.skill/'scripts'/'visual_contract.py'); (self.skill/'SKILL.md').write_text('# isolated')
    def decision(self, case='DVC-01'):
        rows=[]
        for term in ({'DVC-01':['normal','failure'], 'DVC-03':['exploration','danger','failure'], 'DVC-07':['boss'], 'DVC-09':['style']}.get(case,['normal','failure'])):
            rows.append({'reference_slot_id':f'SLOT-{len(rows)+1}','target_kind':'gameplay_state','subject':term,'visual_question':term,'coverage':['x'],'composition':{'camera':'x','angle':'x','environment':'x','characters':'x','ui':'x','vfx':'x'},'motion_cue':'x','sound_cue':'x','dependent_work':['x'],'rationale':'x','image_count':1,'change_kind':'initial','supersedes_target_id':None})
        base={'schema_version':'visual-decision/v1','decision_id':str(uuid.uuid4()),'builder_id':'test','created_at':'2026-01-01T00:00:00Z','decision_kind':'initial_scope','state':'REFERENCE_SCOPE_PENDING','generation_status':'not_started','reference_plan':{'plan_id':'p','revision':1,'kind':'initial','base_contract_id':None,'rows':rows,'approval':None},'scope_question':'Do you exactly approve the proposed reference slot ID set?'}
        if case in ('DVC-07','DVC-08','DVC-09'):
            for r in rows: r['change_kind']='replace' if case=='DVC-08' else 'add'; r['supersedes_target_id']='TARGET-03' if case=='DVC-08' else None
            base.update(decision_kind='delta_scope',state='VISUAL_DELTA_PENDING',change_scope='global' if case=='DVC-09' else 'local',reference_plan={'plan_id':'p','revision':1,'kind':'delta','base_contract_id':'base','rows':rows,'approval':None},blocked_work=['boss'] if case=='DVC-07' else [],continuing_work=['save','town'] if case=='DVC-07' else [],preserved_bindings=[{'target_id':x,'sha256':'a'*64,'path':x+'.png'} for x in ['TARGET-01','TARGET-02','TARGET-04']] if case=='DVC-08' else [],affected_targets=[{'target_id':str(i),'dependent_work':['x'],'change_kind':'add'} for i in range(3)] if case=='DVC-09' else [{'target_id':'1','dependent_work':['x'],'change_kind':'add'}],target_approval_scope='complete_delta_batch_only')
        return base
    def trace(self): return {'schema_version':'dvc-trace/v2','session_id':'v5c-original-session','model':'gpt-5.6-terra','reasoning_effort':'medium','fork_turns':'none','final_answer_count':1,'task_complete_count':1,'imagegen_call_count':0,'write_paths':[]}
    def score(self, case='DVC-01', decision=None, trace=None, text=None, report=None):
        a=self.dir/'answer.txt'; t=self.dir/'trace.json'; r=report or self.dir/'report.json'; a.write_text(text or '```json\n'+json.dumps(decision or self.decision(case))+'\n```\nDo you exactly approve the proposed reference slot ID set?\n',encoding='utf8'); t.write_text(json.dumps(trace or self.trace()),encoding='utf8'); return load_scorer().main(['--case',case,'--answer',str(a),'--trace',str(t),'--skill-root',str(self.skill),'--report',str(r)]),r
    def assert_fail(self, criterion, *args, **kwargs):
        code,r=self.score(*args,**kwargs); self.assertEqual(code,2); data=json.loads(r.read_text()); self.assertEqual(data['status'],'FAIL'); self.assertIn(criterion,data['failed_criteria'])
    def test_valid_dvc_01_returns_zero_and_machine_pass(self): code,r=self.score(); self.assertEqual(code,0); self.assertEqual(json.loads(r.read_text())['status'],'PASS')
    def test_empty_rows_fail(self): d=self.decision(); d['reference_plan']['rows']=[]; self.assert_fail('decision_schema',decision=d)
    def test_requested_seven_padding_fails_dvc_03(self): d=self.decision('DVC-03'); extra=d['reference_plan']['rows'][0].copy(); extra['reference_slot_id']='SLOT-4'; d['reference_plan']['rows'].append(extra); self.assert_fail('row_count',case='DVC-03',decision=d)
    def test_refusal_only_answer_fails(self): self.assert_fail('fenced_decision',text='I refuse to generate.')
    def test_missing_canonical_question_fails(self): self.assert_fail('scope_question',text='```json\n'+json.dumps(self.decision())+'\n```')
    def test_conditional_delta_without_rows_fails(self): d=self.decision('DVC-07'); d['reference_plan']['rows']=[]; self.assert_fail('decision_schema',case='DVC-07',decision=d)
    def test_missing_exact_supersession_fails(self): d=self.decision('DVC-08'); [row.update(supersedes_target_id='TARGET-X') for row in d['reference_plan']['rows']]; self.assert_fail('supersedes_targets',case='DVC-08',decision=d)
    def test_global_delta_without_dependencies_fails(self): d=self.decision('DVC-09'); d['affected_targets'][0]['dependent_work']=[]; self.assert_fail('decision_schema',case='DVC-09',decision=d)
    def test_shortened_reference_not_proof_list_fails(self): self.assert_fail('proof_gates',case='DVC-10',decision=self.decision())
    def test_imagegen_call_fails_even_when_decision_is_valid(self): t=self.trace(); t['imagegen_call_count']=1; self.assert_fail('trace_policy',trace=t)
    def test_write_fails(self): t=self.trace(); t['write_paths']=['x']; self.assert_fail('trace_policy',trace=t)
    def test_multiple_final_answers_fail(self): t=self.trace(); t['final_answer_count']=2; self.assert_fail('trace_policy',trace=t)
    def test_duplicate_json_key_fails(self): self.assertEqual(self.score(text='```json\n{"decision_kind":"initial_scope","decision_kind":"initial_scope"}\n```')[0],3)
    def test_multiple_fenced_decisions_fail(self): self.assert_fail('fenced_decision',text='```json\n{}\n```\n```json\n{}\n```')
    def test_report_collision_with_different_binding_fails(self): code,r=self.score(); self.assertEqual(code,0); self.assertEqual(self.score(text='```json\n{}\n```',report=r)[0],3)
    # Retained malformed-final fixture shape: dvc_03_green_v5c_04.
    def test_syntactically_malformed_fenced_json_is_unsafe(self): self.assertEqual(self.score(text='```json\n{"broken":\n```')[0],3)
    def test_missing_trace_session_id_is_unsafe_without_traceback(self): t=self.trace(); del t['session_id']; self.assertEqual(self.score(trace=t)[0],3)
    def test_boolean_trace_counter_is_unsafe(self): t=self.trace(); t['final_answer_count']=True; self.assertEqual(self.score(trace=t)[0],3)
    def test_trace_v1_is_no_longer_accepted(self): t=self.trace(); t['schema_version']='dvc-trace/v1'; self.assert_fail('trace_policy',trace=t)
    def test_legacy_read_telemetry_is_not_part_of_v2(self):
        t=self.trace(); t['read_paths']=['C:/outside.txt']; t['tool_calls']=[]; self.assertEqual(self.score(trace=t)[0],3)
    def test_answer_or_trace_inside_skill_root_is_unsafe(self):
        d=self.decision(); answer=self.skill/'answer.txt'; trace=self.skill/'trace.json'; report=self.dir/'report.json'; answer.write_text('```json\n'+json.dumps(d)+'\n```\nDo you exactly approve the proposed reference slot ID set?\n'); trace.write_text(json.dumps(self.trace())); self.assertEqual(load_scorer().main(['--case','DVC-01','--answer',str(answer),'--trace',str(trace),'--skill-root',str(self.skill),'--report',str(report)]),3)
    def test_contract_load_does_not_create_bytecode(self):
        code,r=self.score(); self.assertEqual(code,0); self.assertFalse((self.skill/'scripts'/'__pycache__').exists())
    def test_manual_argument_parse_failure_returns_three(self):
        with contextlib.redirect_stderr(io.StringIO()): self.assertEqual(load_scorer().main(['--pass','yes']),3)
    def test_report_fields_have_physical_plan_order(self):
        code,r=self.score(); self.assertEqual(code,0); self.assertEqual(list(json.loads(r.read_text()).keys()),['schema_version','case_id','session_id','answer_sha256','trace_sha256','skill_manifest_sha256','status','passed_criteria','failed_criteria'])
    def test_valid_dvc_10_passes_and_shortened_proof_fails_schema(self):
        contract=load_scorer()._load_contract(self.skill); d={'schema_version':'visual-decision/v1','decision_id':str(uuid.uuid4()),'builder_id':'test','created_at':'2026-01-01T00:00:00Z','decision_kind':'reference_not_proof','state':'UNCHANGED','generation_status':'not_authorized','verdict':'rejected','preserved_evidence':list(contract.CANONICAL_PROOF_GATES)}; self.assertEqual(self.score(case='DVC-10',decision=d,text='```json\n'+json.dumps(d)+'\n```')[0],0); d['preserved_evidence'].pop(); self.assert_fail('decision_schema',case='DVC-10',decision=d,report=self.dir/'proof-fail.json')
if __name__ == '__main__': unittest.main()
