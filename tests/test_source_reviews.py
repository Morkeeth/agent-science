"""Correction review controls with exact synthetic snapshots, no live calls."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from clearance import cases, research, source_metadata, source_reviews, synthesis

BODY = 'The coding tasks were evaluated with a frozen acceptance test and fixed comparator.'
NOTICE = 'This correction changes the table caption only; the coding task results and comparator are unchanged.'


def fixture(db):
    """Reusable synthetic case for actual CLI/MCP review flows."""
    evidence=[dict(id='paper',url='https://doi.org/10.1234/paper',snapshot_text=BODY,snapshot_hash=cases.digest(BODY),status='QUOTE_VERIFIED',kind='research',checked_at='2026-01-01T00:00:00Z'),
              dict(id='notice',url='https://doi.org/10.1234/notice',snapshot_text=NOTICE,snapshot_hash=cases.digest(NOTICE),status='QUOTE_VERIFIED',kind='research',checked_at='2026-01-01T00:00:00Z')]
    cases._save(dict(id='correction-case',version=1,created_at=cases.now(),question='Does the scoped task finding survive the correction?',evidence=evidence,trace=[],decisions=[],provided_sources=[e['url'] for e in evidence],official_domains=[]),db=db)
    data=synthesis.apply('correction-case',1,{'findings':[dict(statement='Coding tasks used a fixed comparator.',relation='supports',rationale='The source explicitly describes this scoped task design.',evidence_id='paper',quote=BODY,strongest_challenge='The correction could change the comparator or evaluated tasks.',what_would_change='An inspected notice changing the task comparator would reverse this assessment.')]},db=db)
    payload=json.dumps({'message':{'DOI':'10.1234/paper','updated-by':[dict(DOI='10.1234/notice',type='correction')]}}).encode()
    with patch.object(source_metadata,'_fetch',return_value=(payload,200)):
        metadata=source_metadata.inspect(data['evidence'][0],live=True)
    data=source_metadata.apply(data['id'],data['version'],'paper',metadata,db=db)
    return data


def proposal(data,db):
    row=source_reviews.list_pending(data['id'],db=db)['pending'][0]
    return {key:row[key] for key in ('assessment_id','evidence_id','source_snapshot_hash','warning_fingerprint')} | dict(disposition='unaffected',rationale='The inspected correction changes the caption and explicitly leaves the comparator unchanged.',notices=[dict(notice_identity='doi:10.1234/notice',evidence_id='notice',quote=NOTICE,snapshot_hash=cases.digest(NOTICE))])


class SourceReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.db=Path(self.temp.name)/'cases.db';self.data=fixture(self.db)
        self.proposal=proposal(self.data,self.db)

    def write(self, mutate):
        data=cases.get(self.data['id'],db=self.db)
        mutate(data); data['version']+=1
        cases._save(data,db=self.db)
        return data

    def submit(self,proposed=None,version=None):
        return source_reviews.review(self.data['id'],version or cases.get(self.data['id'],db=self.db)['version'],proposed or self.proposal,db=self.db)

    def test_scoped_positive_flow_retains_registry_and_history(self):
        before=cases.get(self.data['id'],db=self.db)
        self.assertEqual('REVIEW_REQUIRED',research.brief(before)['claims'][0]['state'])
        self.assertEqual('REVIEW_REQUIRED',synthesis.build(before)['conclusions'][0]['state'])
        result=self.submit();after=cases.get(self.data['id'],db=self.db)
        self.assertEqual([],result['pending']);self.assertEqual(1,len(result['resolved']))
        self.assertEqual('CURRENT',synthesis.build(after)['conclusions'][0]['state'])
        self.assertEqual('SUPPORTED_AS_ASSESSED',research.brief(after)['claims'][0]['state'])
        self.assertEqual(before['evidence'],after['evidence'])
        self.assertEqual('REVIEW_REQUIRED',synthesis.build(cases.get(before['id'],version=before['version'],db=self.db))['conclusions'][0]['state'])
        self.assertTrue(synthesis.compare(before['id'],before['version'],db=self.db)['material_change'])
        self.assertIn('Authored rationale',research.render_brief(research.brief(after)))

    def test_stale_and_fabricated_unrelated_notice_rejected(self):
        for key,value in [('warning_fingerprint','0'*64),('source_snapshot_hash','0'*64)]:
            p=copy.deepcopy(self.proposal);p[key]=value
            with self.subTest(key=key),self.assertRaisesRegex(ValueError,'fingerprint changed'):self.submit(p)
        for field,value in [('quote','This fabricated passage never occurred in the notice.'),('evidence_id','paper'),('snapshot_hash','0'*64),('notice_identity','doi:10.1234/unrelated')]:
            p=copy.deepcopy(self.proposal);p['notices'][0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):self.submit(p)
        self.submit()
        with self.assertRaisesRegex(ValueError,'version changed'):self.submit(version=self.data['version'])

    def test_unavailable_notice_stays_unresolved(self):
        self.write(lambda d:d['evidence'][1].update(status='UNAVAILABLE'))
        with self.assertRaisesRegex(ValueError,'notice_unavailable'):self.submit()
        p=copy.deepcopy(self.proposal);p.update(disposition='unresolved',notices=[],rationale='The registry notice cannot be inspected, so its effect remains unresolved.')
        result=self.submit(p)
        self.assertEqual(1,len(result['pending']));self.assertEqual('unresolved',result['pending'][0]['review']['disposition'])

    def test_review_cannot_rehabilitate_retracted_or_superseded_source(self):
        for field,value in [('retracted',True),('superseded_by','arxiv:2401.00001v2')]:
            self.write(lambda d:d['evidence'][0].update({field:value}))
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'cannot be rehabilitated'):self.submit()
        self.assertEqual('REVIEW_REQUIRED',research.brief(cases.get(self.data['id'],db=self.db))['claims'][0]['state'])

    def test_changed_notice_body_reopens(self):
        self.submit()
        self.write(lambda d:d['evidence'][1].update(snapshot_text=NOTICE+' New affected task.',snapshot_hash=cases.digest(NOTICE+' New affected task.')))
        self.assertEqual(1,len(source_reviews.list_pending(self.data['id'],db=self.db)['pending']))
        self.assertEqual('REVIEW_REQUIRED',synthesis.build(cases.get(self.data['id'],db=self.db))['conclusions'][0]['state'])

    def test_changed_warning_or_source_body_reopens(self):
        self.submit()
        self.write(lambda d:d['evidence'][0]['metadata_review_required'].append(dict(type='correction',notice='doi:10.1234/another',target='doi:10.1234/paper')))
        pending=source_reviews.list_pending(self.data['id'],db=self.db)['pending'][0]
        self.assertNotEqual(self.proposal['warning_fingerprint'],pending['warning_fingerprint'])
        p=copy.deepcopy(self.proposal);p['warning_fingerprint']=pending['warning_fingerprint']
        with self.assertRaisesRegex(ValueError,'all registry notices'):self.submit(p)
        self.write(lambda d:d['evidence'][0].update(snapshot_text=BODY+' Changed body.',snapshot_hash=cases.digest(BODY+' Changed body.')))
        self.assertEqual('REVIEW_REQUIRED',synthesis.build(cases.get(self.data['id'],db=self.db))['conclusions'][0]['state'])

    def test_reassessment_does_not_inherit_acknowledgment(self):
        self.submit();data=cases.get(self.data['id'],db=self.db);claim=data['claims'][0]
        data=research.assess(data['id'],data['version'],statement=None,claim_id=claim['id'],relation='supports',rationale='A newly authored interpretation must review its own correction scope.',evidence_id='paper',quote=BODY,supersedes=claim['assessments'][0]['id'],db=self.db)
        self.assertEqual('REVIEW_REQUIRED',research.brief(data)['claims'][0]['state'])
        self.assertEqual(1,len(source_reviews.list_pending(data['id'],db=self.db)['pending']))
        with self.assertRaisesRegex(ValueError,'active assessment'):self.submit()

    def test_later_revise_reopens_without_changing_claim(self):
        self.submit();before=cases.get(self.data['id'],db=self.db)
        p=copy.deepcopy(self.proposal);p.update(disposition='revise',rationale='On further reading the table caption may alter the interpretation of task scope.')
        result=self.submit(p)
        self.assertEqual(1,len(result['pending']));self.assertEqual(2,len(result['reviews']))
        self.assertEqual(before['claims'],cases.get(self.data['id'],db=self.db)['claims'])

    def test_resolution_does_not_clear_other_assessment(self):
        data=research.assess(self.data['id'],self.data['version'],statement='Another task claim needs its own review.',relation='context',rationale='This interpretation has a different scope from the comparator claim.',evidence_id='paper',quote=BODY,db=self.db)
        result=self.submit()
        self.assertEqual(1,len(result['resolved']));self.assertEqual(1,len(result['pending']))
        self.assertNotEqual(result['resolved'][0]['assessment_id'],result['pending'][0]['assessment_id'])

    def test_malformed_json_fields_have_validation_errors(self):
        for field in ('notice_identity','evidence_id','snapshot_hash'):
            p=copy.deepcopy(self.proposal);p['notices'][0][field]={'not':'text'}
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,'nonempty text'):self.submit(p)
        p=copy.deepcopy(self.proposal);p['disposition']={'bad':'type'}
        with self.assertRaisesRegex(ValueError,'disposition'):self.submit(p)

    def test_condition_warning_resolves_only_its_assessment_scope(self):
        self.write(lambda d:d['claims'][0]['assessments'][0].update(conditions=[dict(field='task',value='coding tasks',anchor=dict(evidence_id='paper',quote=BODY,snapshot_hash=cases.digest(BODY),url='https://doi.org/10.1234/paper'))]))
        self.submit()
        data=cases.get(self.data['id'],db=self.db)
        conclusion=synthesis.build(data)['conclusions'][0]
        self.assertEqual('CURRENT',conclusion['conditions'][0]['state'])
        self.write(lambda d:d['claims'][0]['assessments'][0]['conditions'][0].update(value='different interpretation'))
        self.assertEqual('REVIEW_REQUIRED',synthesis.build(cases.get(self.data['id'],db=self.db))['conclusions'][0]['state'])

    def test_latest_unresolved_survives_source_body_reversion(self):
        self.submit()
        changed=BODY+' A later source revision.'
        self.write(lambda d:d['evidence'][0].update(snapshot_text=changed,snapshot_hash=cases.digest(changed)))
        pending=source_reviews.list_pending(self.data['id'],db=self.db)['pending'][0]
        p=copy.deepcopy(self.proposal);p.update(source_snapshot_hash=pending['source_snapshot_hash'],disposition='unresolved',notices=[],rationale='The later source revision makes the correction effect unresolved.')
        self.submit(p)
        self.write(lambda d:d['evidence'][0].update(snapshot_text=BODY,snapshot_hash=cases.digest(BODY)))
        result=source_reviews.list_pending(self.data['id'],db=self.db)
        self.assertEqual([],result['resolved'])
        self.assertEqual('unresolved',result['pending'][0]['review']['disposition'])
        self.assertEqual('REVIEW_REQUIRED',synthesis.build(cases.get(self.data['id'],db=self.db))['conclusions'][0]['state'])

    def test_conflicting_notice_redirect_identity_cannot_cover_two_notices(self):
        current=cases.get(self.data['id'],db=self.db)
        payload=json.dumps({'message':{'DOI':'10.1234/paper','updated-by':[dict(DOI=doi,type='correction') for doi in ('10.1234/notice','10.1234/another')]}}).encode()
        with patch.object(source_metadata,'_fetch',return_value=(payload,200)):
            metadata=source_metadata.inspect(current['evidence'][0],live=True)
        source_metadata.apply(current['id'],current['version'],'paper',metadata,db=self.db)
        self.write(lambda d:d['evidence'][1].update(final_url='https://doi.org/10.1234/another'))
        p=proposal(cases.get(self.data['id'],db=self.db),self.db)
        p['notices'].append(dict(notice_identity='doi:10.1234/another',evidence_id='notice',quote=NOTICE,snapshot_hash=cases.digest(NOTICE)))
        with self.assertRaisesRegex(ValueError,'ambiguous'):self.submit(p)

    def test_review_response_is_pinned_despite_concurrent_later_revision(self):
        real=source_reviews.list_pending
        def racing(case_id,*,db=None,version=None):
            data=cases.get(case_id,db=db);data['version']+=1
            data['evidence'][0].update(snapshot_text=BODY+' Concurrent change.',snapshot_hash=cases.digest(BODY+' Concurrent change.'))
            cases._save(data,db=db)
            return real(case_id,db=db,**({'version':version} if version is not None else {}))
        with patch.object(source_reviews,'list_pending',racing):result=self.submit()
        self.assertEqual(result['reviews'][-1]['recorded_version'],result['version'])
        self.assertEqual(1,len(result['resolved']))
        self.assertGreater(cases.get(self.data['id'],db=self.db)['version'],result['version'])

    def test_notice_errors_name_fixable_cause(self):
        failures=[('notice_quote_absent',{},dict(quote='This passage never appeared inside the actual correction notice.')),
                  ('notice_snapshot_stale',{},dict(snapshot_hash='0'*64)),
                  ('notice_unavailable',dict(status='UNAVAILABLE'),{}),
                  ('notice_needs_review',dict(metadata_review_required=[dict(type='correction',notice='doi:10.1234/third')]),{}),
                  ('notice_retracted',dict(retracted=True),{}),
                  ('notice_body_hash_mismatch',dict(snapshot_hash='0'*64),dict(snapshot_hash='0'*64))]
        original=copy.deepcopy(self.data['evidence'][1])
        for reason,changes,anchor_changes in failures:
            with self.subTest(reason=reason):
                self.write(lambda d:d['evidence'].__setitem__(1,{**original,**changes}))
                p=copy.deepcopy(self.proposal);p['notices'][0].update(anchor_changes)
                with self.assertRaisesRegex(ValueError,reason):self.submit(p)


    def test_malformed_warning_remains_pending(self):
        self.write(lambda d:d['evidence'][0].update(metadata_review_required=True))
        result=source_reviews.list_pending(self.data['id'],db=self.db)
        self.assertEqual(1,len(result['pending']))
        self.assertEqual('REVIEW_REQUIRED',synthesis.build(cases.get(self.data['id'],db=self.db))['conclusions'][0]['state'])

    def test_notice_error_rows_show_why_prior_resolution_reopened(self):
        self.submit()
        self.write(lambda d:d['evidence'][1].update(retracted=True))
        pending=source_reviews.list_pending(self.data['id'],db=self.db)['pending'][0]
        self.assertEqual('notice_retracted',pending['notice_failures'][0]['reason'])
        self.assertTrue(pending['review_binding_current'])

    def test_withdrawn_removed_and_partial_retraction_are_not_acknowledgments(self):
        for kind in ('withdrawal','removal','partial_retraction','expression_of_concern'):
            with self.subTest(kind=kind):
                db=Path(self.temp.name)/(kind+'.db');data=fixture(db)
                payload=json.dumps({'message':{'DOI':'10.1234/paper','updated-by':[dict(DOI='10.1234/notice',type=kind)]}}).encode()
                with patch.object(source_metadata,'_fetch',return_value=(payload,200)):
                    metadata=source_metadata.inspect(data['evidence'][0],live=True)
                data=source_metadata.apply(data['id'],data['version'],'paper',metadata,db=db)
                self.assertFalse(data['evidence'][0].get('retracted',False))
                p=proposal(data,db)
                if kind=='expression_of_concern':
                    self.assertEqual(1,len(source_reviews.review(data['id'],data['version'],p,db=db)['resolved']))
                else:
                    with self.assertRaisesRegex(ValueError,'cannot be rehabilitated'):
                        source_reviews.review(data['id'],data['version'],p,db=db)
                    self.assertEqual('REVIEW_REQUIRED',synthesis.build(data)['conclusions'][0]['state'])

    def test_same_doi_mirror_inherits_warning_and_needs_separate_assessment_review(self):
        self.write(lambda d:d['evidence'].append(dict(id='mirror',url='https://dx.doi.org/10.1234/paper?download=pdf',snapshot_text=BODY,snapshot_hash=cases.digest(BODY),status='QUOTE_VERIFIED',kind='research')))
        data=cases.get(self.data['id'],db=self.db)
        data=research.assess(data['id'],data['version'],statement='A mirror assessment shares the study warning.',relation='supports',rationale='This mirror represents the exact same DOI and study.',evidence_id='mirror',quote=BODY,db=self.db)
        self.assertEqual('REVIEW_REQUIRED',research.brief(data)['claims'][-1]['state'])
        pending=source_reviews.list_pending(data['id'],db=self.db)['pending']
        mirror=next(row for row in pending if row['evidence_id']=='mirror')
        self.assertEqual(['paper'],mirror['warning_inherited_from'])
        self.submit()
        self.assertEqual('REVIEW_REQUIRED',research.brief(cases.get(data['id'],db=self.db))['claims'][-1]['state'])

    def test_same_study_mirror_cannot_be_its_own_notice(self):
        self.write(lambda d:d['evidence'].append(dict(id='mirror',url='https://dx.doi.org/10.1234/paper?download=pdf',snapshot_text=NOTICE,snapshot_hash=cases.digest(NOTICE),status='QUOTE_VERIFIED',kind='research')))
        data=cases.get(self.data['id'],db=self.db)
        payload=json.dumps({'message':{'DOI':'10.1234/paper','updated-by':[dict(DOI='10.1234/paper',type='correction')]}}).encode()
        with patch.object(source_metadata,'_fetch',return_value=(payload,200)):
            metadata=source_metadata.inspect(data['evidence'][0],live=True)
        data=source_metadata.apply(data['id'],data['version'],'paper',metadata,db=self.db)
        p=proposal(data,self.db)
        p['notices'].append(dict(notice_identity='doi:10.1234/paper',evidence_id='mirror',quote=NOTICE,snapshot_hash=cases.digest(NOTICE)))
        with self.assertRaisesRegex(ValueError,'notice_same_study'):self.submit(p)

    def test_arxiv_supersession_applies_only_to_exact_old_version(self):
        old=dict(id='old',url='https://arxiv.org/abs/2401.00001v1',snapshot_text=BODY,snapshot_hash=cases.digest(BODY),status='QUOTE_VERIFIED',metadata_review_required=[dict(type='new-version',target='arxiv:2401.00001',target_version='arxiv:2401.00001v1',notice='arxiv:2401.00001v2')],superseded_by='arxiv:2401.00001v2')
        mirror=dict(id='old-pdf',url='https://arxiv.org/pdf/2401.00001v1',snapshot_text=BODY,snapshot_hash=cases.digest(BODY),status='QUOTE_VERIFIED')
        newer=dict(id='new',url='https://arxiv.org/abs/2401.00001v2',snapshot_text=BODY,snapshot_hash=cases.digest(BODY),status='QUOTE_VERIFIED')
        data=dict(evidence=[old,mirror,newer])
        self.assertEqual(['new-version'],source_reviews._non_rehabilitable(source_reviews.effective_source(data,mirror)))
        self.assertFalse(source_reviews.effective_source(data,newer).get('metadata_review_required'))
        self.assertFalse(source_reviews.effective_source(data,dict(newer,id='unknown',url='https://arxiv.org/abs/2401.00001')).get('metadata_review_required'))

    def test_unresolved_binds_exact_missing_snapshot_without_invented_hash(self):
        self.write(lambda d:d['evidence'][0].update(snapshot_text=None,snapshot_hash=None,status='UNAVAILABLE'))
        row=source_reviews.list_pending(self.data['id'],db=self.db)['pending'][0]
        p=copy.deepcopy(self.proposal);p.update(source_snapshot_hash=row['source_snapshot_hash'],disposition='unresolved',notices=[],rationale='The source snapshot is unavailable and the correction effect remains unknown.')
        result=self.submit(p)
        self.assertIsNone(result['reviews'][-1]['source_snapshot_hash'])
        self.assertEqual(1,len(result['pending']))
        for disposition in ('unaffected','revise'):
            p['disposition']=disposition
            with self.subTest(disposition=disposition),self.assertRaisesRegex(ValueError,'only unresolved'):self.submit(p)
        p.update(disposition='unresolved',source_snapshot_hash='invented')
        with self.assertRaisesRegex(ValueError,'fingerprint changed'):self.submit(p)
