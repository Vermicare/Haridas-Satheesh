"""30-second local-only demonstration of actual child-process commit-window kills."""
import json
from test_atomic_process_kill_v15 import AtomicProcessKillTests


def snapshot(point):
    case = AtomicProcessKillTests('test_kill_before_sink_ack_commit_rolls_back_both')
    case.setUp()
    try:
        case.kill_child(point)
        return case.adapter.counts(case.nonce)
    finally:
        case.doCleanups()


if __name__ == '__main__':
    before = snapshot('before')
    after = snapshot('after')
    assert before == {'status': 'pending', 'fictional_sink_rows': 0, 'external_actions': 0}
    assert after == {'status': 'acked', 'fictional_sink_rows': 1, 'external_actions': 0}
    print(json.dumps({
        'experiment': 'fictional-atomic-process-kill-v15',
        'synthetic': True,
        'before_commit_kill': before,
        'after_commit_kill': after,
        'external_actions': 0,
        'physical_power_loss_tested': False,
        'legacy_bypass_eliminated': False,
    }, sort_keys=True))
