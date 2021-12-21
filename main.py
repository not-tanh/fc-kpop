import math
import traceback
from datetime import datetime

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image

from objects.player import Positions, Player
from objects.match import Match
from objects.debt import Debt
from db.player_api import create_player, get_players, update_player
from db.match_api import get_matches, create_match, update_match
from db.stats_api import get_stats
from db.debt_api import get_debt, create_debt, delete_debt

st.set_page_config('FC KPop', layout='wide', page_icon=':soccer:')
page = st.sidebar.radio('', ('Trang chủ', 'Admin'))

POSITION_LIST = [Positions.Goalkeeper.value, Positions.Defender.value,
                 Positions.Midfielder.value, Positions.Striker.value]
MEDAL_ICONS = [':first_place_medal:', ':second_place_medal:', ':third_place_medal:']
IMAGE_SIZE = (200, 200)

ID_TO_PLAYER = dict()
for player in get_players():
    ID_TO_PLAYER[player['_id']] = player['name']

ID_TO_IMAGE = dict()
for player in get_players():
    if player.get('photo', None):
        try:
            ID_TO_IMAGE[player['_id']] = Image.frombytes('RGB', IMAGE_SIZE, player['photo'].encode('latin-1'))
        except:
            ID_TO_IMAGE[player['_id']] = Image.frombytes('L', IMAGE_SIZE, player['photo'].encode('latin-1'))

ID_TO_DEBT = dict()
debts = get_debt()
for did in debts:
    for detail in debts[did]['detail']:
        ID_TO_DEBT[detail['_id']] = f'{ID_TO_PLAYER[detail["player_id"]]} ' \
                                    f'{detail["value"]}k {detail["desc"]} ngày {detail["date"].date()}'


def format_player(name):
    return ID_TO_PLAYER[name]


def add_player_form():
    with st.form('add_player'):
        name = st.text_input('Tên cầu thủ')
        alias = st.text_input('Tên thi đấu')
        yob = st.number_input('Năm sinh', min_value=1980, max_value=2021)
        number = st.number_input('Số áo', min_value=1, max_value=99)
        position = st.selectbox('Vị trí', POSITION_LIST)
        photo = st.file_uploader('Ảnh')
        submit = st.form_submit_button('Thêm')
        if submit:
            if not name or not alias or not yob or not number or not photo:
                st.error('Cần điền đủ thông tin')
            else:
                photo = Image.open(photo)
                photo = photo.resize(IMAGE_SIZE).tobytes().decode('latin-1')

                player = Player(name, alias, yob, number, position, photo)
                try:
                    create_player(player)
                    st.success(f'Thêm cầu thủ {name} thành công')
                except:
                    st.error('Có lỗi xảy ra')


def update_player_form():
    players = get_players()
    if len(players):
        selected_player_name = st.selectbox('Chọn cầu thủ', [p['name'] for p in players])
        selected_id = ''
        selected_index = -1
        for i, player in enumerate(players):
            if selected_player_name == player['name']:
                selected_id = player['_id']
                selected_index = i
                break

        with st.form('edit_player'):
            name = st.text_input('Tên cầu thủ', players[selected_index]['name'])
            alias = st.text_input('Tên thi đấu', players[selected_index]['alias'])
            yob = st.number_input('Năm sinh', min_value=1980, max_value=2021, value=players[selected_index]['yob'])
            number = st.number_input('Số áo', min_value=1, max_value=99, value=players[selected_index]['number'])
            position = st.selectbox(
                'Vị trí', POSITION_LIST, index=POSITION_LIST.index(players[selected_index]['position'])
            )
            current_photo = ID_TO_IMAGE.get(players[selected_index]['_id'], None)
            if current_photo:
                photo = st.image(current_photo, caption='Ảnh hiện tại')
            new_photo = st.file_uploader('Tải ảnh mới')
            submit = st.form_submit_button('Cập nhật')
            if submit:
                if not name or not alias or not yob or not number:
                    st.error('Cần điền đủ thông tin')
                else:
                    photo = photo if new_photo is None else new_photo
                    if photo:
                        photo = Image.open(photo)
                        photo = photo.resize(IMAGE_SIZE).tobytes().decode('latin-1')

                    player = Player(name, alias, yob, number, position, photo)
                    try:
                        update_player(selected_id, player)
                        st.success(f'Cập nhật cầu thủ {name} thành công')
                    except:
                        traceback.print_exc()
                        st.error('Có lỗi xảy ra')
    else:
        st.info('Không có cầu thủ nào')


def update_match_form():
    matches = get_matches()
    if len(matches):
        selected_opponent = st.selectbox('Chọn trận đấu', [p['opponent'] for p in matches])
        selected_id = ''
        selected_index = -1
        for i, match in enumerate(matches):
            if selected_opponent == match['opponent']:
                selected_id = match['_id']
                selected_index = i
                break

        with st.form('edit_match'):
            date = st.date_input('Ngày thi đấu', matches[selected_index]['date'])
            match_time = st.text_input('Giờ thi đấu', matches[selected_index].get('time', ''))
            opponent = st.text_input('Đối', matches[selected_index]['opponent'])
            stadium = st.text_input('Sân', matches[selected_index].get('stadium', ''))
            uniform = st.text_input('Đồng phục', matches[selected_index].get('uniform', ''))
            scored = st.number_input('Bàn thắng', min_value=0, max_value=100,
                                     value=matches[selected_index].get('scored', 0))
            conceded = st.number_input('Bàn bại', min_value=0, max_value=100,
                                       value=matches[selected_index].get('conceded', 0))
            cost = st.number_input('Tiền sân', min_value=0, value=matches[selected_index].get('cost', 0))
            player_num = st.number_input('Số người đá', min_value=0, max_value=25,
                                         value=matches[selected_index].get('player_num', 0))

            score_list = st.multiselect('Người ghi bàn', get_player_ids() * 10, format_func=format_player,
                                        default=matches[selected_index].get('score_list', []))
            assist_list = st.multiselect('Người kiến tạo', get_player_ids() * 10, format_func=format_player,
                                         default=matches[selected_index].get('assist_list', []))
            submit = st.form_submit_button('Cập nhật')
            if submit:
                if not stadium or not match_time or not uniform or not opponent:
                    st.error('Cần điền đủ thông tin')
                    return
                else:
                    date = datetime.combine(date, datetime.min.time())
                    match = Match(date=date, opponent=opponent, scored=scored, conceded=conceded,
                                  score_list=score_list, assist_list=assist_list, time=match_time,
                                  stadium=stadium, uniform=uniform, cost=cost, player_num=player_num)
                    try:
                        update_match(selected_id, match)
                        st.success(f'Cập nhật trận đấu với {opponent} thành công')
                    except:
                        traceback.print_exc()
                        st.error('Có lỗi xảy ra')
    else:
        st.info('Không có trận đấu nào để cập nhật')


def add_match_form():
    matches = get_matches()
    old_opponent_list = list(set([m['opponent'] for m in matches]))

    with st.form('add_match'):
        date = st.date_input('Ngày thi đấu')
        match_time = st.text_input('Giờ thi đấu')
        old_opponent = st.selectbox('Đối cũ', ['---'] + old_opponent_list)
        new_opponent = st.text_input('Đối mới')
        stadium = st.text_input('Sân')
        uniform = st.text_input('Đồng phục')
        scored = st.number_input('Bàn thắng', min_value=0, max_value=100)
        conceded = st.number_input('Bàn bại', min_value=0, max_value=100)
        cost = st.number_input('Tiền sân', min_value=0)
        player_num = st.number_input('Số người đá', min_value=0, max_value=25)

        score_list = st.multiselect('Người ghi bàn', get_player_ids() * 10, format_func=format_player)
        assist_list = st.multiselect('Người kiến tạo', get_player_ids() * 10, format_func=format_player)
        submit = st.form_submit_button('Thêm trận đấu')

        if submit:
            if new_opponent.strip():
                opponent = new_opponent
            elif old_opponent != '---':
                opponent = old_opponent
            else:
                st.error('Chưa điền thông tin đối')
                return
            if not stadium or not match_time or not uniform:
                st.error('Cần điền đủ thông tin về giờ, sân và đồng phục')
                return
            date = datetime.combine(date, datetime.min.time())
            match = Match(date=date, opponent=opponent, scored=scored, conceded=conceded,
                          score_list=score_list, assist_list=assist_list, time=match_time,
                          stadium=stadium, uniform=uniform, cost=cost, player_num=player_num)
            try:
                create_match(match)
                st.success(f'Thêm trận đấu với {opponent} thành công')
            except:
                st.error('Có lỗi xảy ra')


def add_debt_form():
    with st.form('add_debt'):
        date = st.date_input('Ngày')
        players = st.multiselect('Người nợ', get_player_ids(), format_func=format_player)
        value = st.number_input('Tổng tiền')
        desc = st.text_input('Ghi chú')
        submit = st.form_submit_button('Thêm con nợ')

        if submit:
            if not players or not value or not desc:
                st.error('Chưa điền đủ thông tin')
                return
            else:
                date = datetime.combine(date, datetime.min.time())
                value_per_player = math.ceil(float(value) / len(players))
                try:
                    for player in players:
                        new_debt = Debt(player, date=date, value=value_per_player, desc=desc)
                        create_debt(new_debt)
                    st.success(f'Thêm các con nợ thành công')
                except:
                    st.error('Có lỗi xảy ra')


def delete_debt_form():
    debts = get_debt()

    with st.form('delete_debt'):
        checkboxes = dict()
        for did in debts:
            for detail in debts[did]['detail']:
                checkboxes[detail['_id']] = st.checkbox(ID_TO_DEBT[detail['_id']])
        submit = st.form_submit_button('Xóa')
        if submit:
            delete_ids = [did for did in checkboxes if checkboxes[did]]
            try:
                if delete_ids:
                    delete_debt(delete_ids)
                    st.caching.clear_memo_cache()
                    st.success('Xóa nợ thành công')
                else:
                    st.error('Chưa chọn khoản nợ nào')
            except:
                traceback.print_exc()
                st.error('Xoá nợ thành công')


def show_schedule():
    st.subheader('Lịch thi đấu :date:')
    matches = get_matches()
    for m in matches:
        del m['_id']
        m['score_list'] = ', '.join([ID_TO_PLAYER[x] for x in m['score_list']])
        m['assist_list'] = ', '.join([ID_TO_PLAYER[x] for x in m['assist_list']])
        m['player_num'] = 0 if m.get('player_num', 0) == 0 else m.get('player_num')
        m['cost'] = 0 if m.get('cost', 0) == 0 else m.get('cost')
        m['date'] = m['date'].date()

    matches_df = pd.DataFrame.from_dict(matches).rename(
        columns={'date': 'Ngày thi đấu', 'time': 'Giờ thi đấu', 'opponent': 'Đối', 'stadium': 'Sân',
                 'uniform': 'Đồng phục', 'scored': 'Bàn thắng', 'conceded': 'Bàn bại', 'score_list': 'Ghi bàn',
                 'assist_list': 'Kiến tạo', 'cost': 'Tiền sân', 'player_num': 'Số người đá'}
    )
    st.table(matches_df.assign(hack='').set_index('hack'))


def show_team():
    cols = st.columns([2, 1, 1])
    cols[0].subheader('Danh sách đội :spiral_note_pad:')
    players = get_players()
    for p in players:
        del p['_id']
        if 'photo' in p:
            del p['photo']
    df = pd.DataFrame.from_dict(players).rename(
        columns={'name': 'Tên', 'alias': 'Tên thi đấu', 'yob': 'Năm sinh', 'number': 'Số áo', 'position': 'Vị trí'}
    )
    cols[0].table(df.assign(hack='').set_index('hack'))

    # define data
    win, lose, tie = all_stats['win_count'], all_stats['lose_count'], all_stats['tie_count']
    total_goals, total_conceded = all_stats['total_goals'], all_stats['total_conceded']

    label_form = ['Thắng', 'Thua', 'Hòa']
    label_goals_conceded = ['Bàn thắng', 'Bàn thua']

    colors_1 = sns.color_palette('pastel')[0:3]
    fig_1, ax_1 = plt.subplots()
    ax_1.pie([win, lose, tie], colors=colors_1, autopct='%.0f%%')
    ax_1.legend(label_form, loc='lower left')
    ax_1.set_title('Phong độ')
    cols[1].pyplot(fig_1)

    colors_2 = sns.color_palette('pastel')[3:5]
    fig_2, ax_2 = plt.subplots()
    ax_2.pie([total_goals, total_conceded], colors=colors_2, autopct='%.0f%%')
    ax_2.legend(label_goals_conceded, loc='lower left')
    ax_2.set_title('Bàn thắng - Bàn thua')
    cols[2].pyplot(fig_2)


def get_player_names():
    return [player['name'] for player in get_players()]


def get_player_ids():
    return [player['_id'] for player in get_players()]


def spacer():
    st.text('')


if page == 'Trang chủ':
    all_stats = get_stats()
    goal_stats, assist_stats = all_stats['most_goals'], all_stats['most_assists']

    st.title(':soccer: Chào mừng bạn đến với trang web của FC KPop :soccer:')

    show_schedule()
    spacer()

    show_team()
    spacer()
    spacer()

    st.subheader(':star: Ngôi sao của FC KPop :star:')
    spacer()

    title_columns = st.columns(2)
    title_columns[0].subheader('Vua phá lưới :athletic_shoe:')
    title_columns[1].subheader('Ông hoàng kiến tạo :goal_net:')

    star_columns = st.columns(6)

    for i, (pid, goals) in enumerate(goal_stats):
        if ID_TO_IMAGE.get(pid, None):
            star_columns[i].image(ID_TO_IMAGE[pid])
        star_columns[i].write(f'{MEDAL_ICONS[i]} {ID_TO_PLAYER[pid]} đã ghi {goals} bàn thắng')

    for i, (pid, assists) in enumerate(assist_stats):
        if ID_TO_IMAGE.get(pid, None):
            star_columns[i + 3].image(ID_TO_IMAGE[pid])
        star_columns[i + 3].write(f'{MEDAL_ICONS[i]} {ID_TO_PLAYER[pid]} đã kiến tạo {assists} lần')
    spacer()
    spacer()

    info_header_cols = st.columns([2, 3, 1])

    info_cols = st.columns([2, 3, 1])
    info_header_cols[0].subheader('Bạn muốn bón hành cho chúng tôi? Liên hệ ngay :phone:')
    info_cols[0].write('Đội trưởng Sờ Mít Râu: https://www.facebook.com/duong.kip')

    debt = get_debt()
    info_header_cols[1].subheader('Bốc bát họ')
    if not debt:
        info_cols[1].write('Không ai có nợ')
    else:
        table_data = []

        for player_id in debt:
            tmp = {'Tên': ID_TO_PLAYER[player_id], 'Nợ': debt[player_id]['sum']}
            detail_text = []
            for detail in debt[player_id]['detail']:
                detail_text.append(f'{detail["date"].date()}: {detail["value"]}k {detail["desc"]}')
            tmp['Chi tiết'] = ' | '.join(detail_text)
            table_data.append(tmp)
        df = pd.DataFrame.from_records(table_data)
        info_cols[1].table(df.assign(hack='').set_index('hack'))

    info_header_cols[-1].subheader('Thông tin chuyển khoản')
    info_cols[-1].write('Ngân hàng :bank: Vietcombank')
    info_cols[-1].write('STK :1234: 0021000393362')
    info_cols[-1].write('Tên :credit_card: Nguyễn Tuấn Anh')

else:
    st.title('Trang quản lý')
    password = st.text_input('Mật khẩu', type='password')
    if password:
        if password == st.secrets['ADMIN_PASSWORD']:
            def format_tab(option):
                tmp = {
                    'add_player': 'Thêm cầu thủ', 'update_player': 'Cập nhật thông tin cầu thủ',
                    'add_match': 'Thêm trận đấu', 'update_match': 'Cập nhật thông tin trận đấu',
                    'add_debt': 'Thêm con nợ', 'delete_debt': 'Xóa nợ'
                }
                return tmp[option]

            tab = st.radio('', ('add_player', 'update_player', 'add_match', 'update_match', 'add_debt', 'delete_debt'),
                           format_func=format_tab)
            st.subheader(format_tab(tab))
            if tab == 'add_player':
                add_player_form()
            elif tab == 'update_player':
                update_player_form()
            elif tab == 'add_match':
                add_match_form()
            elif tab == 'update_match':
                update_match_form()
            elif tab == 'add_debt':
                add_debt_form()
            elif tab == 'delete_debt':
                delete_debt_form()
        else:
            st.error('Thích mò mật khẩu không thằng lòn? Máy mày sẽ bị dính virus :)')
