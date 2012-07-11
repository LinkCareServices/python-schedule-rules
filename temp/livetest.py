# coding: utf-8
import datetime
from schedule import Session, SRules, Interval, CalculatedSession
from dateutil.relativedelta import relativedelta
from dateutil import rrule

ses1 = Session("Test1", duration=60*8,start_hour=13, start_minute=30)
ses1.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,20), interval = 2, until=datetime.date(2012,1,1))

ses2 = Session("Test2", duration=60*3,start_hour=12, start_minute=00)
ses2.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,25), interval = 1, until=datetime.date(2012,1,1))

ses3 = Session("Test3", duration=60*3,start_hour=12, start_minute=00)
ses3.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,8,25), interval = 5, until=datetime.date(2012,1,1))

ses4 = Session("Test4", duration=30,start_hour=13, start_minute=00)
ses4.add_rule("", freq=rrule.DAILY, dtstart=datetime.date(2011,12,20), interval = 1, until=datetime.date(2012,1,15))

ses_p = Session("Test", duration=60*8,start_hour=13, start_minute=30)
ses_p.add_rule("1er jour des 6", 
             freq=rrule.DAILY,
             dtstart=datetime.date(2011,8,20), 
             interval=6,
             until = datetime.date(2012,8,30)  
            )
ses_p.add_rule("2eme jour des 6", 
             freq=rrule.DAILY,
             dtstart=datetime.date(2011,8,20)+relativedelta(days=+1), 
             interval=6,
             until = datetime.date(2012,8,30)  
            )
ses_p.add_rule("3eme jour des 6", 
             freq=rrule.DAILY,
             dtstart=datetime.date(2011,8,20)+relativedelta(days=+2), 
             interval=6,
             until = datetime.date(2012,8,30)  
            )
ses_p2 = Session("Test2", duration=60*3,start_hour=11, start_minute=30)
ses_p2.add_rule("Tous les jours", 
             freq=rrule.DAILY,
             dtstart=datetime.date(2011,8,30), 
             interval=1,
             until = datetime.date(2011,12,30)  
            )
result_list = ses_p - ses_p2

srule = SRules("Test",True)
srule.add_session(ses1)
srule.add_session(ses2)
