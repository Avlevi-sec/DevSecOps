#the standalone python script to be used over in Azure functions service in order to renew transfer status expired requests.
import logging
import azure.functions as func
import os
from keepercommander import api,cli
from keepercommander.commands.enterprise import UserReportCommand
from keepercommander.params import KeeperParams
import pandas as pd
from io import StringIO
import tempfile


app = func.FunctionApp()

@app.schedule(schedule="*/30  * * * *", arg_name="myTimer", run_on_startup=True,
              use_monitor=False) 
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    tempFilePath = tempfile.gettempdir()
    my_params = KeeperParams(config_filename=f'{tempFilePath}/config.json')
    my_params.user = os.getenv("keeper_user")
    my_params.password = os.getenv("keeper_pass")
    #check connections strings thing
    users_list = []
    api.login(my_params)
    api.sync_down(my_params)
    response_content = cli.do_command(my_params,"ei --users --columns transfer_status --format csv")
    response_file = StringIO(response_content)
    df = pd.read_csv(response_file)
    logging.info(df)
    cli.do_command(my_params,f"logout")
    logging.info("keeper log out successfull")
    
