# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import math
import platform
import asyncio

import aiopyupbit

import utils
import config
from static import log
import static
import component


def press_any_key() -> None:
    """프롬프트 아무키나 입력 기능
    """
    try:
        # Windows용 코드
        import msvcrt
        msvcrt.getch()

    except ImportError:
        # Linux & Mac 용 코드
        import sys
        import tty
        import termios

        fd = sys.stdin.fileno()
        original_attributes = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, original_attributes)


def print_program_title() -> None:
    """프롬프트 타이틀 출력
    """
    try:
        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')
    except KeyboardInterrupt as e:
        pass
    print(f'\t┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓')
    print(
        f'\t┃                          {config.PROGRAM["NAME"]} :: Version {config.PROGRAM["VERSION"]}                          ┃')
    print(
        f'\t┃                          Websocket sync thread status - {"● Enabled" if static.chart.alive else "Χ Disabled"}                                ┃')
    print(f'\t┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛')


def print_menu() -> None:
    """프롬프트 메뉴 출력
    """
    print_program_title()
    print("\t1. Total Price")
    print("\t2. Individual Price")
    print("\t3. Holding List")
    print("\t8. Websocket Sync Start")
    print("\t9. Websocket Sync Stop")
    print("\t0. Exit or CTRL + C")


def print_total_price() -> None:
    """코인 전체 현재 가격 정보 출력
    """
    while True:
        try:
            print_program_title()
            print('\t', end='')
            for _ in range(0, 4):
                print(f'│ Code       Price       ', end='')
            print()
            count = 0
            for coin in static.chart.coins.values():
                if count == 0:
                    print('\t', end='')
                print(
                    f'│ {coin.code:<10} {coin.get_trade_price():<12.2f}', end='')
                count += 1
                if count == 4:
                    print()
                    count = 0
            print('\n\t[CTRL + C] Exit to menu')
            time.sleep(0.5)
        except:
            break


def print_individual_price() -> None:
    """코인 개별 정보 출력
    """
    while True:
        print_program_title()
        count = 0
        codes = []
        for coin in static.chart.coins.values():
            if count % 5 == 0:
                print('\t', end='')
            print(f'│ {count + 1:>3}. {coin.code:<13}', end='')
            codes.append(coin.get_code())
            count += 1
            if count % 5 == 0:
                print()

        print('\n\t0. [CTRL + C] Exit to menu')
        try:
            select = input("\t> ")
        except KeyboardInterrupt as e:
            break
        except Exception as e:
            break

        try:
            if select == '':
                continue
            elif int(select) == 0:
                break
            else:
                print_trade_information(
                    static.chart.coins[codes[int(select) - 1]])
        except IndexError as e:
            print('\tOut of index, please enter to continue...')
            press_any_key()
        except UnboundLocalError as e:
            break


def print_trade_information(_coin: component.Coin) -> None:
    """코인 거래 상세 정보 출력

    Args:
        _coin (Coin): 출력할 코인
    """
    while True:
        try:

            if _coin.get_signed_change_price() > 0:
                condition = '▲'
            elif _coin.get_signed_change_price() < 0:
                condition = '▼'
            else:
                condition = '●'

            print_program_title()
            print(
                f'\t│ Code: {_coin.get_code():<22}   │ High(52W): [{_coin.get_highest_52_week_date()}] {_coin.get_highest_52_week_price()} ')
            print(
                f'\t│ Cuttent Price: {_coin.get_trade_price():<15} │ Low(52W):  [{_coin.get_lowest_52_week_date()}] {_coin.get_lowest_52_week_price()} ')
            print(
                f'\t│ Open: {_coin.get_opening_price():<24} │ High(1D): {_coin.get_high_price():<20} │ Trade Volume(24H): {_coin.get_acc_trade_volume_24h():.3f}')
            print(f'\t│ Change: {_coin.get_signed_change_rate() * 100:>6.2f}% {condition} {_coin.get_signed_change_price():<12} │ Low(1D): {_coin.get_low_price():<21} │ Trade Price(24H): {_coin.get_acc_trade_price_24h():.0f}')
            print(f'\t├────────────────────────────────────────── Order Book')
            print(
                f'\t│                         Volume             Ask │ Bid             Volume')
            for unit in reversed(_coin.get_orderbook_units()):
                if _coin.get_trade_price() == unit["bp"]:
                    print(
                        f'\t│ ★{round(unit["as"], 3):>29} {unit["ap"]:>15} │')
                else:
                    print(f'\t│ {round(unit["as"], 3):>30} {unit["ap"]:>15} │')
            for unit in _coin.get_orderbook_units():
                if _coin.get_trade_price() == unit["ap"]:
                    print(
                        f'\t│                                                │ {unit["bp"]:<15} {round(unit["bs"], 3):<29}★')
                else:
                    print(
                        f'\t│                                                │ {unit["bp"]:<15} {round(unit["bs"], 3):<30}')
            print(f'\t│ {round(_coin.get_total_ask_size(), 3):>30}               Total               {round(_coin.get_total_bid_size(), 3):<30}')
            print('\t[CTRL + C] Exit to menu')
            time.sleep(0.5)
        except KeyboardInterrupt as e:
            break
        except Exception as e:
            break


def print_holding_list() -> None:
    """사용자 투자 코인 내역 출력
    """
    while True:
        try:
            total_purchase = 0
            total_avaluate = 0

            print_program_title()
            print('\t│ Code  Count                 Avg Buy         Purchase        Avaluate        Loss            Yield')
            for item in asyncio.run(static.upbit.get_balances()):
                currency = item["currency"]
                balance = float(item["balance"])
                if currency == 'XYM':
                    continue

                if currency == 'KRW':
                    print(f'\t│ {currency:<5} {math.floor(balance):<21}')
                    total_purchase += balance
                    total_avaluate += balance
                else:
                    purchase = round(balance * float(item["avg_buy_price"]), 0)
                    avaluate = round(balance * static.chart.get_coin("%s-%s" %
                                                                     (config.FIAT, currency)).get_trade_price(), 0)
                    loss = avaluate - purchase
                    total_purchase += purchase
                    total_avaluate += avaluate
                    print(
                        f'\t│ {currency:<5} {balance:<21} {item["avg_buy_price"]:<15} {purchase:<15.0f} {avaluate:<15.0f} {loss:<15.0f} {((avaluate / purchase) - 1) * 100:<7.2f}%')
            print(f'\t│\n\t│ Total Purchase: {total_purchase:.0f}')
            print(f'\t│ Total Avaluate: {total_avaluate:.0f}')
            print(f'\t│ Total Loss    : {total_avaluate - total_purchase:.0f}')
            print(
                f'\t│ Total Yield   : {((total_avaluate / total_purchase) - 1) * 100:.2f} %')

            print('\t[CTRL + C] Exit to menu')
            time.sleep(5)
        except KeyboardInterrupt as e:
            break
        # except Exception as e:
        #     break


def prompt_main() -> None:
    """프롬프트 메인
    """
    while True:
        print_menu()
        try:
            select = input("\t> ")
        except KeyboardInterrupt as e:
            print("\n\tProgram terminating...")
            exit()
        except Exception as e:
            print("\n\tProgram terminating...")
            exit()

        if select == '':
            continue
        elif int(select) == 0:
            exit()
        elif int(select) == 1:
            print_total_price()
        elif int(select) == 2:
            print_individual_price()
        elif int(select) == 3:
            print_holding_list()
        elif int(select) == 8:
            if not static.chart.alive:
                static.chart.start()
            else:
                print('\tWebsocket sync thread already enabled...')
                press_any_key()
        elif int(select) == 9:
            if static.chart.alive:
                static.chart.stop()
            else:
                print('\tWebsocket sync thread already disabled...')
                press_any_key()
        else:
            print('\tOut of index, please enter to continue...')
            press_any_key()


if __name__ == '__main__':
     
    utils.set_windows_selector_event_loop_global()
    
    # Upbit coin chart
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    codes = loop.run_until_complete(aiopyupbit.get_tickers(fiat=config.FIAT, contain_name=True))
    static.chart = component.RealtimeManager(codes=codes)
    static.chart.start()

    # User upbit connection
    static.upbit = aiopyupbit.Upbit(
        config.UPBIT["ACCESS_KEY"], config.UPBIT["SECRET_KEY"])

    prompt_main()
