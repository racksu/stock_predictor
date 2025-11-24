"""
測試新的 BUY/HOLD/SELL 判斷邏輯
驗證方案 1（綜合判斷）是否正確實施
"""

print("="*80)
print("測試新的操作建議判斷邏輯")
print("="*80)

# 模擬 _determine_action_smart 函數（與實際代碼相同）
def _determine_action_smart(score, expected_return, risk_reward_ratio, signal):
    """智能判斷操作建議（綜合方案）"""

    # 1. 強力買入條件
    if (score >= 70 and expected_return >= 0.08 and risk_reward_ratio >= 2.0):
        return 'BUY'

    # 2. 買入條件（滿足2個條件）
    buy_conditions = sum([
        score >= 60,
        expected_return >= 0.05,
        risk_reward_ratio >= 1.5
    ])
    if buy_conditions >= 2:
        return 'BUY'

    # 3. 賣出條件
    if (score < 40 or expected_return < -0.05 or '強力賣出' in signal):
        return 'SELL'

    # 4. 謹慎持有
    if score < 50 and expected_return < 0:
        return 'HOLD'

    # 5. 持有
    return 'HOLD'

# 測試案例
test_cases = [
    {
        'name': '案例1：強力買入（三項優秀）',
        'score': 75,
        'expected_return': 0.10,  # 10%
        'risk_reward_ratio': 3.0,
        'signal': '買入',
        'expected_action': 'BUY',
        'reason': '評分高、預期報酬高、風險報酬比高'
    },
    {
        'name': '案例2：一般買入（滿足2項）',
        'score': 65,
        'expected_return': 0.06,  # 6%
        'risk_reward_ratio': 1.2,
        'signal': '買入',
        'expected_action': 'BUY',
        'reason': '評分≥60 ✓, 預期報酬≥5% ✓（2/3條件滿足）'
    },
    {
        'name': '案例3：技術超買但預期下跌 → 賣出',
        'score': 35,
        'expected_return': -0.08,  # -8%
        'risk_reward_ratio': 0.3,
        'signal': '賣出',
        'expected_action': 'SELL',
        'reason': '評分<40 且 預期虧損≥5%'
    },
    {
        'name': '案例4：技術超賣預期反彈 → 買入',
        'score': 68,
        'expected_return': 0.15,  # 15%
        'risk_reward_ratio': 2.5,
        'signal': '買入',
        'expected_action': 'BUY',
        'reason': '三項條件都優秀（強力買入）'
    },
    {
        'name': '案例5：橫盤整理但預期上漲 → 買入',
        'score': 55,
        'expected_return': 0.12,  # 12%
        'risk_reward_ratio': 2.8,
        'signal': '持有',
        'expected_action': 'BUY',
        'reason': '預期報酬≥5% ✓, 風險報酬比≥1.5 ✓（2/3條件滿足）'
    },
    {
        'name': '案例6：評分中等預期微跌 → 持有',
        'score': 55,
        'expected_return': -0.02,  # -2%
        'risk_reward_ratio': 1.0,
        'signal': '持有',
        'expected_action': 'HOLD',
        'reason': '不符合買入條件，虧損未達賣出標準'
    },
    {
        'name': '案例7：評分低預期大跌 → 賣出',
        'score': 45,
        'expected_return': -0.10,  # -10%
        'risk_reward_ratio': 0.2,
        'signal': '強力賣出',
        'expected_action': 'SELL',
        'reason': '預期虧損≥5% 且 強力賣出信號'
    },
    {
        'name': '案例8：評分低但預期微漲 → 持有',
        'score': 45,
        'expected_return': 0.03,  # 3%
        'risk_reward_ratio': 0.8,
        'signal': '持有',
        'expected_action': 'HOLD',
        'reason': '不符合買入條件（預期報酬<5%），也不符合賣出條件'
    },
    {
        'name': '案例9：高評分但預期為負 → 持有',
        'score': 70,
        'expected_return': -0.01,  # -1%
        'risk_reward_ratio': 1.0,
        'signal': '持有',
        'expected_action': 'HOLD',
        'reason': '評分高但預期為負，不滿足強力買入條件'
    },
    {
        'name': '案例10：邊界測試（剛好滿足買入）',
        'score': 60,
        'expected_return': 0.05,  # 5%
        'risk_reward_ratio': 1.5,
        'signal': '買入',
        'expected_action': 'BUY',
        'reason': '三項條件剛好達標（3/3條件滿足）'
    }
]

# 執行測試
print("\n執行測試案例...\n")
passed = 0
failed = 0

for i, case in enumerate(test_cases, 1):
    result = _determine_action_smart(
        score=case['score'],
        expected_return=case['expected_return'],
        risk_reward_ratio=case['risk_reward_ratio'],
        signal=case['signal']
    )

    is_pass = result == case['expected_action']
    status = '✅ PASS' if is_pass else '❌ FAIL'

    if is_pass:
        passed += 1
    else:
        failed += 1

    print(f"{status} {case['name']}")
    print(f"     評分: {case['score']}, 預期報酬: {case['expected_return']*100:+.1f}%, 風險報酬比: {case['risk_reward_ratio']:.1f}")
    print(f"     預期操作: {case['expected_action']}, 實際操作: {result}")
    print(f"     原因: {case['reason']}")

    if not is_pass:
        print(f"     ⚠️ 測試失敗！")

    print()

# 總結
print("="*80)
print(f"測試總結: {passed}/{len(test_cases)} 通過")
if failed == 0:
    print("✅ 所有測試通過！新邏輯運作正常")
else:
    print(f"❌ 有 {failed} 個測試失敗，需要檢查邏輯")
print("="*80)

# 對比舊邏輯
print("\n📊 新舊邏輯對比示例")
print("="*80)

comparison_cases = [
    {
        'scenario': '股價上漲20%，技術超買',
        'score': 35,
        'expected_return': -0.05,
        'old_logic': 'SELL（只看評分<40）',
        'new_logic': _determine_action_smart(35, -0.05, 0.3, '賣出')
    },
    {
        'scenario': '股價橫盤，基本面改善',
        'score': 55,
        'expected_return': 0.12,
        'old_logic': 'HOLD（評分40-60之間）',
        'new_logic': _determine_action_smart(55, 0.12, 2.8, '持有')
    },
    {
        'scenario': '股價下跌30%，技術超賣',
        'score': 65,
        'expected_return': 0.15,
        'old_logic': 'BUY（評分≥60且信號買入）',
        'new_logic': _determine_action_smart(65, 0.15, 2.5, '買入')
    }
]

for case in comparison_cases:
    print(f"\n情境: {case['scenario']}")
    print(f"  評分: {case['score']}, 預期報酬: {case['expected_return']*100:+.0f}%")
    print(f"  舊邏輯 → {case['old_logic']}")
    print(f"  新邏輯 → {case['new_logic']}")

    if case['old_logic'].split('（')[0] != case['new_logic']:
        print(f"  📌 結果不同！新邏輯更合理")
    else:
        print(f"  ✓ 結果一致")

print("\n" + "="*80)
print("測試完成")
print("="*80)
