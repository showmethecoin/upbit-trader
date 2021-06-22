# !/usr/bin/python
# -*- coding: utf-8 -*-
import os
import time
import platform
import asyncio as aio

import aiopyupbit

from component import Coin
import static
import strategy


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
    except KeyboardInterrupt:
        pass
    print(f'\t┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓')
    print(
        f'\t┃                          Upbit Automatic Trading Program :: Version {static.config.program_version}                          ┃')
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
    print("\t4. Volatility breakout strategy test")
    print("\t5. Various indicator strategy test")
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
        except KeyboardInterrupt:
            break
        except Exception:
            break

        try:
            if select == '':
                continue
            elif int(select) == 0:
                break
            else:
                print_trade_information(
                    static.chart.coins[codes[int(select) - 1]])
        except IndexError:
            print('\tOut of index, please enter to continue...')
            press_any_key()
        except UnboundLocalError:
            break


def print_trade_information(_coin: Coin) -> None:
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
        except KeyboardInterrupt:
            break
        except Exception:
            break


def print_holding_list() -> None:
    """사용자 투자 코인 내역 출력
    """
    while True:
        try:
            print_program_title()
            print('\t│ Code  Count                 Avg Buy         Purchase        Evaluate        Loss            Yield')
            print(f'\t│ KRW   {int(static.account.get_total_cash()):<21,}')
            for code, data in static.account.coins.items():
                balance = data['balance']
                locked = data['locked']
                avg_buy_price = data['avg_buy_price']
                purchase = data['purchase']
                evaluate = data['evaluate']
                loss = data['loss']
                coin_yield = data['yield']
                print(f'\t| {code:<5} {balance + locked:<21,} {(lambda x: x if x < 100 else int(x))(avg_buy_price):<15,} {int(purchase):<15,} {int(evaluate):<15,} {int(loss):<15,} {coin_yield:<7.2f}%')
            print(
                f'\t│\n\t│ Total Purchase: {static.account.get_buy_price():.0f}')
            print(
                f'\t│ Total Evaluate: {static.account.get_evaluate_price():.0f}')
            print(f'\t│ Total Loss    : {static.account.get_total_loss():.0f}')
            print(
                f'\t│ Total Yield   : {static.account.get_total_yield():.2f} %')
            print('\t[CTRL + C] Exit to menu')
            time.sleep(1)
        #except KeyboardInterrupt:
            #break
        except Exception as e:
            print(e)
            break


def prompt_main() -> None:
    """프롬프트 메인
    """
    while True:
        print_menu()
        try:
            select = input("\t> ")
        except KeyboardInterrupt:
            print("\n\tProgram terminating...")
            exit()
        except Exception:
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
        elif int(select) == 4:
            static.strategy = strategy.VolatilityBreakoutStrategy(
                queue=static.signal_queue)
            static.strategy.start()
        elif int(select) == 5:
            static.strategy = strategy.VariousIndicatorStrategy(
                queue=static.signal_queue)
            static.strategy.start()
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
    from component import RealtimeManager, Account
    from config import Config
    from utils import set_windows_selector_event_loop_global

    set_windows_selector_event_loop_global()

    static.config = Config()
    static.config.load()

    loop = aio.new_event_loop()
    aio.set_event_loop(loop)
    codes = loop.run_until_complete(
        aiopyupbit.get_tickers(fiat=static.FIAT, contain_name=True))
    static.chart = RealtimeManager(codes=codes)
    static.chart.start()

    # Upbit account
    static.account = Account(access_key=static.config.upbit_access_key,
                             secret_key=static.config.upbit_secret_key)
    static.account.start()

    prompt_main()
