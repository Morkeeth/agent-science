"""Real Git worktrees and real external Python checks; no model/provider calls."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

from clearance import cases, context_trials as trials, research_protocols, research


def sha(data):
    return hashlib.sha256(data).hexdigest()


class ContextTrials(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'; self.repo.mkdir()
        self.git('init'); self.git('config', 'user.email', 'test@example.invalid'); self.git('config', 'user.name', 'Test')
        (self.repo / 'AGENTS.md').write_text('Baseline instructions')
        (self.repo / 'code.py').write_text('value = 0\n')
        self.git('add', '.'); self.git('commit', '-m', 'base')
        self.pin = self.git('rev-parse', 'HEAD').strip()
        self.db = str(self.root / 'cases.db')
        self.case = cases.create('Does instruction context change the accepted fix?', db=self.db)
        self.case = research.assess(self.case['id'], self.case['version'], statement='Instruction effects remain unresolved.', relation='unresolved', rationale='No agent trial has been performed.', db=self.db)
        self.script = self.root / 'check.py'; self.script.write_text("from pathlib import Path\nraise SystemExit(0 if 'value = 1' in Path('code.py').read_text() else 1)\n")
        self.baseline = self.root / 'baseline.md'; self.baseline.write_text('Baseline instructions')
        self.candidate = self.root / 'candidate.md'; self.candidate.write_text('Candidate instructions')
        protocol = research_protocols.create(self.case['id'], dict(kind='agent_context_trial', hypothesis='Task-matched instruction intervention', claim_refs=[dict(claim_id=self.case['claims'][0]['id'], version=self.case['version'])], repo=str(self.repo), tasks=['Fix the value under the frozen contract.'], baseline='Original instructions', intervention='Candidate instructions', outcomes=['Accepted fixes'], budget=dict(runs=2,timeout=30,basis='Four attempts'), stopping_rule='All fixed slots or budget exhausted',check_sha256=sha(self.script.read_bytes())), db=self.db)
        self.spec=dict(protocol_id=protocol['id'],protocol_version=1,repo=str(self.repo),base_commit=self.pin,
            tasks=[dict(id='fix',prompt='Fix the value under the frozen contract.',acceptance_task='fix')],
            arms=[dict(id=name,instructions_path=str(path),sha256=sha(path.read_bytes())) for name,path in [('baseline',self.baseline),('candidate',self.candidate)]],
            acceptance_path=str(self.script),acceptance_sha256=sha(self.script.read_bytes()),host=dict(provider='native',model='unknown',identity='fresh-host-session'),
            policy=dict(max_attempts=4,total_seconds=140,attempt_seconds=30,check_seconds=5),repetitions=2,artifact_root=str(self.root/'artifacts'))

    def git(self,*args):
        return subprocess.check_output(['git','-C',str(self.repo),*args],stderr=subprocess.DEVNULL,text=True)

    def start(self):
        return trials.create(self.spec,db=self.db)

    def prepare(self,trial,**kwargs):
        return trials.prepare(trial['id'],task_id='fix',arm_id='baseline',repetition=1,expected_version=trial['version'],trusted=True,db=self.db,**kwargs)

    def complete(self,trial):
        return trials.complete(trial['id'],trial['attempts'][-1]['id'],expected_version=trial['version'],trusted=True,db=self.db)

    def test_actual_tree_patch_and_acceptance(self):
        trial=self.prepare(self.start()); tree=Path(trial['attempts'][0]['worktree'])
        self.assertEqual(self.pin,subprocess.check_output(['git','-C',str(tree),'rev-parse','HEAD'],text=True).strip())
        (tree/'code.py').write_text('value = 1\n')
        done=self.complete(trial)
        self.assertEqual('ACCEPTED',done['attempts'][0]['state'])
        self.assertEqual(1,done['summary']['accepted'])
        self.assertEqual('value = 0\n',(self.repo/'code.py').read_text())
        with self.assertRaisesRegex(ValueError,'no blind retry'):
            self.complete(done)

    def test_noop_and_failed_fix_never_success(self):
        done=self.complete(self.prepare(self.start()))
        self.assertEqual('INVALID',done['attempts'][0]['state'])
        self.assertEqual(0,done['summary']['accepted'])
        trial=self.prepare(self.start()); Path(trial['attempts'][0]['worktree'],'code.py').write_text('value = 2\n')
        done=self.complete(trial)
        self.assertEqual('REJECTED',done['attempts'][0]['state'])
        self.assertEqual(0,done['summary']['accepted'])

    def test_wrong_hash_and_unknown_identity(self):
        self.spec['acceptance_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'hash differs'):
            self.start()
        self.spec['acceptance_sha256']=sha(self.script.read_bytes()); self.spec['host']['identity']='unknown'
        with self.assertRaisesRegex(ValueError,'known'):
            self.start()

    def test_stale_duplicate_and_trust(self):
        trial=self.start()
        with self.assertRaisesRegex(ValueError,'acknowledgement'):
            trials.prepare(trial['id'],task_id='fix',arm_id='baseline',repetition=1,expected_version=1,db=self.db)
        prepared=self.prepare(trial)
        with self.assertRaisesRegex(ValueError,'stale'):
            self.prepare(trial)
        with self.assertRaisesRegex(ValueError,'already reserved'):
            self.prepare(prepared)

    def test_modified_check_and_instructions(self):
        trial=self.prepare(self.start()); tree=Path(trial['attempts'][0]['worktree']); (tree/'code.py').write_text('value = 1\n')
        Path(trial['manifest']['acceptance_path']).write_text('raise SystemExit(0)')
        done=self.complete(trial)
        self.assertEqual('INVALID',done['attempts'][0]['state'])
        self.assertNotIn('acceptance',done['attempts'][0]['result'])

    def test_expired_host_and_cancel_retains_denominator(self):
        trial=self.prepare(self.start())
        def expire(body): body['attempts'][0]['started_epoch']=time.time()-100
        trial=trials._update(trial['id'],trial['version'],expire,self.db)
        done=self.complete(trial); self.assertEqual('TIMEOUT',done['attempts'][0]['state'])
        other=self.prepare(self.start())
        done=trials.abort(other['id'],other['attempts'][0]['id'],expected_version=other['version'],reason='Host interrupted',trusted=True,db=self.db)
        self.assertEqual('CANCELLED',done['attempts'][0]['state']); self.assertEqual(4,done['summary']['denominator'])

    def test_real_timeout_bounded_output(self):
        script=self.root/'slow.py';script.write_text("import time\nprint('x'*100000,flush=True)\ntime.sleep(10)\n")
        result=trials._run_check(script,'fix',self.repo,0.2,self.root/'out.txt')
        self.assertTrue(result['timed_out']); self.assertLessEqual((self.root/'out.txt').stat().st_size,65536)
        self.assertLess(result['elapsed_seconds'],3)

    def test_changed_instructions_rejected_before_check(self):
        trial=self.prepare(self.start()); tree=Path(trial['attempts'][0]['worktree'])
        (tree/'code.py').write_text('value = 1\n'); (tree/'AGENTS.md').write_text('changed')
        done=self.complete(trial)
        self.assertEqual('INVALID',done['attempts'][0]['state'])
        self.assertNotIn('acceptance',done['attempts'][0]['result'])

    def test_duplicate_patch_flag_preserves_separate_actual_attempts(self):
        trial=self.prepare(self.start()); tree=Path(trial['attempts'][0]['worktree'])
        (tree/'code.py').write_text('value = 1\n'); trial=self.complete(trial)
        trial=trials.prepare(trial['id'],task_id='fix',arm_id='baseline',repetition=2,expected_version=trial['version'],trusted=True,db=self.db)
        Path(trial['attempts'][-1]['worktree'],'code.py').write_text('value = 1\n')
        done=self.complete(trial)
        self.assertEqual('ACCEPTED',done['attempts'][-1]['state'])
        self.assertTrue(done['attempts'][-1]['result']['duplicate_patch_hash'])
        self.assertTrue(done['attempts'][-1]['result']['acceptance_passed'])
        self.assertEqual(2,done['summary']['accepted'])

    def test_capacity_reservation_is_not_refunded(self):
        self.spec['policy']['max_attempts']=1
        trial=self.prepare(self.start())
        trial=trials.abort(trial['id'],trial['attempts'][0]['id'],expected_version=trial['version'],reason='Host stopped',trusted=True,db=self.db)
        with self.assertRaisesRegex(ValueError,'capacity exhausted'):
            trials.prepare(trial['id'],task_id='fix',arm_id='candidate',repetition=1,expected_version=trial['version'],trusted=True,db=self.db)
