#!/usr/bin/env python
import asyncio
import aiomoex
import pandas as pd


async def main():
    async with aiomoex.ISSClientSession():
        # data = await aiomoex.get_board_history('SNGSP')
        #df = pd.DataFrame(data)
        #df.set_index('TRADEDATE', inplace=True)
        #print(df.head(), '\n')
        #print(df.tail(), '\n')
        # df.info()
        data = await aiomoex.find_securities('SBER', columns=('secid',
                                                              'boardid',
                                                              'isin',
                                                              'latname',
                                                              'regnumber'))
        df = pd.DataFrame(data)
        print(df.head(), '\n')
        print(df.tail(), '\n')
        # print(df)


def aiomoex():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()


if __name__ == '__main__':
    aiomoex()
