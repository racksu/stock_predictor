"""
生成帶checkbox的篩選條件HTML
"""

# 定義所有篩選條件
filters = [
    # 價格與報酬組
    {
        'group': '價格與報酬',
        'items': [
            {
                'id': 'price',
                'label': '現價範圍',
                'type': 'range',
                'min_default': '0',
                'max_default': '9999',
                'min_val': '0',
                'max_val': '99999',
                'step': '10'
            },
            {
                'id': 'return',
                'label': '預期報酬率 (%)',
                'type': 'range',
                'min_default': '-100',
                'max_default': '100',
                'min_val': '-100',
                'max_val': '100',
                'step': '5'
            },
            {
                'id': 'target',
                'label': '目標價範圍',
                'type': 'range',
                'min_default': '0',
                'max_default': '9999',
                'min_val': '0',
                'max_val': '99999',
                'step': '10'
            }
        ]
    },
    # 風險與流動性組
    {
        'group': '風險與流動性',
        'items': [
            {
                'id': 'rr',
                'label': '風險報酬比',
                'type': 'range',
                'min_default': '0',
                'max_default': '10',
                'min_val': '0',
                'max_val': '10',
                'step': '0.5'
            },
            {
                'id': 'rel-vol',
                'label': '相對成交量',
                'type': 'range',
                'min_default': '0',
                'max_default': '10',
                'min_val': '0',
                'max_val': '10',
                'step': '0.5'
            },
            {
                'id': 'liquidity',
                'label': '流動性評級',
                'type': 'select',
                'options': [
                    ('all', '全部'),
                    ('極高', '極高'),
                    ('高', '高'),
                    ('中等', '中等'),
                    ('低', '低'),
                    ('極低', '極低')
                ]
            }
        ]
    },
    # 時間與其他組
    {
        'group': '時間與其他',
        'items': [
            {
                'id': 'days',
                'label': '達成時間 (天)',
                'type': 'range',
                'min_default': '0',
                'max_default': '365',
                'min_val': '0',
                'max_val': '365',
                'step': '10'
            },
            {
                'id': 'avg-vol',
                'label': '平均成交量',
                'type': 'range',
                'min_default': '0',
                'max_default': '999999999',
                'min_val': '0',
                'max_val': '999999999',
                'step': '10000'
            }
        ]
    }
]

# 生成範圍輸入HTML
def generate_range_html(item_id, item):
    return f'''                            <div class="filter-item">
                                <label class="filter-label">
                                    <input type="checkbox" class="filter-checkbox" id="enable-{item_id}" onchange="toggleFilter('screen-min-{item_id}', this.checked)">
                                    <span class="filter-label-text">{item['label']}</span>
                                </label>
                                <div class="range-inputs">
                                    <div class="input-with-buttons">
                                        <button class="adjust-btn" onclick="adjustValue('screen-min-{item_id}', -{item['step']})" data-target="screen-min-{item_id}">−</button>
                                        <input type="number" id="screen-min-{item_id}" value="{item['min_default']}" min="{item['min_val']}" max="{item['max_val']}" step="{item['step']}" disabled placeholder="最低">
                                        <button class="adjust-btn" onclick="adjustValue('screen-min-{item_id}', {item['step']})" data-target="screen-min-{item_id}">+</button>
                                    </div>
                                    <span class="range-separator">至</span>
                                    <div class="input-with-buttons">
                                        <button class="adjust-btn" onclick="adjustValue('screen-max-{item_id}', -{item['step']})" data-target="screen-max-{item_id}">−</button>
                                        <input type="number" id="screen-max-{item_id}" value="{item['max_default']}" min="{item['min_val']}" max="{item['max_val']}" step="{item['step']}" disabled placeholder="最高">
                                        <button class="adjust-btn" onclick="adjustValue('screen-max-{item_id}', {item['step']})" data-target="screen-max-{item_id}">+</button>
                                    </div>
                                </div>
                            </div>
'''

# 生成下拉選擇HTML
def generate_select_html(item_id, item):
    options_html = '\n'.join([f'                                    <option value="{val}">{text}</option>'
                               for val, text in item['options']])
    return f'''                            <div class="filter-item">
                                <label class="filter-label">
                                    <input type="checkbox" class="filter-checkbox" id="enable-{item_id}" onchange="toggleFilter('screen-{item_id}', this.checked)">
                                    <span class="filter-label-text">{item['label']}</span>
                                </label>
                                <select id="screen-{item_id}" class="form-select" disabled>
{options_html}
                                </select>
                            </div>
'''

# 生成所有HTML
print("<!-- 以下是生成的篩選條件HTML -->\n")

for group in filters:
    print(f'''                        <!-- {group['group']} -->
                        <div class="filter-group">
                            <div class="filter-group-title">{'⚖️' if group['group'] == '風險與流動性' else '💰' if group['group'] == '價格與報酬' else '⏰'} {group['group']}</div>
''')

    for item in group['items']:
        item_id = item['id']
        if item['type'] == 'range':
            print(generate_range_html(item_id, item))
        elif item['type'] == 'select':
            print(generate_select_html(item_id, item))

    print('                        </div>\n')

print("\n<!-- 生成完成 -->")
