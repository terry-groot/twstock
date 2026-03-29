import os
import sys
from pprint import pprint

#for twstock, please install 'twstock' and 'lxml' modules 
import twstock
import datetime

# for figure plot, please install 'matplotlib'
#import matplotlib.pyplot as plb

def get_realtime_stock_info(id):
   #stock_id = input("Input the stock ID: ")
    stock_id = id
    stock_info = twstock.realtime.get(stock_id)
    pprint(stock_info)
    '''
    if stock_info['success']:
        s_id    = f"{stock_id}"
        s_time  = f"{stock_info['info']['time']}" 
        s_price = f"{stock_info['realtime']['latest_trade_price']}"
        s_open  = f"{round(float(stock_info['realtime']['open']),1)}"
        s_low   = f"{round(float(stock_info['realtime']['low']),1)}"
        s_high  = pf"{round(float(stock_info['realtime']['high']),1)}"
        s_vol   = f"{stock_info['realtime']['accumulate_trade_volume']}"
        print(f"Stock ID : {s_id}")
        print(f"Time     : {s_time}")
        print(f"Price    : {s_price}, {s_open}, {s_low}, {s_high}")
        print(f"Volume   : {s_vol}")
    else:
        print(f"Error, Get stock ({stock_id}) info fail !!")
    '''
#stocklist = tsmc_stock.fetch(datetime.date.today().year, datetime.date.today().month)
#for s in stocklist:
#    print(s)

#print(twstock.__file__)

def main():
    os.system('clear')
    if len(sys.argv) != 2:
        print("Error, Usage: python3 xxx.py <stock_id>")
        sys.exit()

    id = sys.argv[1]
    get_realtime_stock_info(id)

if __name__ == "__main__":
    main()

