from json.decoder import JSONDecodeError
from gevent import monkey as curious_george
curious_george.patch_all(thread=False, select=False)

import os
from csv import reader
from datetime import datetime
import raritySniperFunctions as r
from dotenv import load_dotenv
from discord.ext import commands
import time
import discord
from web3 import Web3
from pytz import timezone
tz = timezone('EST')




def makeBands(project_info, proxy_list):

    startTime = datetime.now()
    project_info = r.formatProjectDic(project_info)

    r.makeCsv(project_info)
    #r.scoreToken(project_info)
    r.checkBuyPrice(project_info, proxy_list)

    print(datetime.now() - startTime)
    return project_info


def main():

    project_info = {}

    # change to your directory where the project is stored
    directory_path = 'ENTER_DIRECTORY'

    # change to the contract address of the project
    contract = "ENTER_CONTRACT"

    #change to the total supply function on 
    correct_supply = "totalSupply"
    #correct_supply = "MAX_SUPPLY"


    project_info["correct_supply"] = correct_supply
    project_info["contract"] = contract
    project_info["directory_path"] = directory_path

    load_dotenv('bot.env')
    TOKEN = os.getenv('DISCORD_TOKEN')
    bot = commands.Bot(command_prefix='!')

    project_info = r.getProjectData(project_info)
    print(project_info)
    proxy_list = r.getProxy()
    project_info = makeBands(project_info, proxy_list)

    

    # @bot.command(name='pull')
    # async def nine_nine(ctx):

    #     #getReveal(contract)

    #     project_info = getProjectData(contract)
    #     print(project_info)

    #     project_info['directory_path'] = directory_path
    #     proxy_list = getProxy()

    #     project_info = makeBands(project_info, proxy_list, contract)
    #     print(project_info)

    #     for_sale_file_path = project_info['for_sale_file_path']

    #     total_errors = getError(project_info)

    #     await ctx.send(f'There were {total_errors} errors when trying to evaluate the token')
        
    #     count = 0
    #     with open(for_sale_file_path, 'r') as read_obj:
    #         csv_reader = reader(read_obj)
    #         for row in csv_reader:
    #             if count == 0:
    #                 count = count + 1
    #                 continue
    #             if count == 52:
    #                 break
    #             rank = row[0]
    #             token = row[1]
    #             image = row[3]
    #             price = row[4]
    #             link = row[5]
    #             if price != "":
    #                 await ctx.send(f'{token} ranked at #{rank} is for sale at {price}. Buy it here {link}. Check image to be sure {image}')
    #             count += 1

    #     await ctx.send(file=discord.File(for_sale_file_path))
    # bot.run(TOKEN)    

if __name__ == "__main__":
    main()

 
