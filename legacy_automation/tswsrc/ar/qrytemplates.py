


LQM1 = '''select q.url_id, priority from u2..url_state us (NOLOCK), u2..queue q (NOLOCK) where us.url_id=q.url_id and us.state_id=1 and q.queue!=86 and  q.queue!=352 and q.cur_level=3 and scheduled_count=0'''
LQM_ADD1 = '''update url_state set state_id=1, scheduled_count=0 where url_id in (select top 20000 us.url_id from url_state us, queue q where us.url_id=q.url_id and q.queue!=86 and q.queue!=352)'''
LQM_ADD1 = '''update queue set cur_level=3 where url_id in (select top 20000 q.url_id from url_state us, queue q where us.url_id=q.url_id and scheduled_count=0 and state_id=1 and q.queue!=86 and q.queue!=352)'''

WORKTASK_TWEAK = 'update WorkTask set dispatchCount=0,dispatchdate=null,completeDate=null,message=null,returnCode=null,priority=99999 '
QUEUE_TWEAK = 'update [u2].[dbo].[queue] set cur_level=3,priority=99999 '
URLSTATE_TWEAK = 'update url_state set state_id=1,scheduled_count=0 '





class CleanUp:
    """ """

