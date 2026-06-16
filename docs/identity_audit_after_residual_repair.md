# Identity Audit Report

- Generated at: `2026-06-14T01:10:32`
- Local DB: `D:\SSH\环境游戏程序\healing-environment\data\healing.db`
- Feishu enabled: `True`

## Local Summary

- Users: `13`
- HCI participants: `8`
- Sessions: `715`
- Duplicate user name+gender groups: `1`
- Duplicate participant name+gender groups: `0`
- Mismatched user/participant codes: `0`
- Users without HCI participant row: `5`

### Local Target Participants

```json
[]
```

## Feishu Summary

- Participant table: `tblOpqLdd7QB9GCS`
- Participant records: `20`
- Duplicate name groups: `0`
- Duplicate name+gender groups: `0`
- Duplicate code groups: `0`
- Missing identity rows: `0`

### Feishu Target Participants

```json
[
  {
    "record_id": "recvlACkqO3dYX",
    "participant_code": "0002",
    "registered_name": "Arya",
    "registered_name_key": "arya",
    "gender": "女",
    "user_id": "8",
    "local_id": "5",
    "updated_at": 1781236475000,
    "raw_fields": {
      "中心编号": "社区",
      "创建时间": 1780583531000,
      "参与者编号": "0002",
      "年龄段": "30~39",
      "性别": "女",
      "教育层级": "未填写",
      "更新时间": 1781236475000,
      "本地参与者ID": "5",
      "本地用户ID": "8",
      "登记姓名": "Arya",
      "研究阶段": "未填写",
      "诊断大类": "其他/未填写"
    }
  },
  {
    "record_id": "recvmj3AZ8ZEJx",
    "participant_code": "0127",
    "registered_name": "20260612-1",
    "registered_name_key": "20260612-1",
    "gender": "女",
    "user_id": "18",
    "local_id": "18",
    "updated_at": 1781323649000,
    "raw_fields": {
      "中心编号": "浦江",
      "创建时间": 1781243829000,
      "参与者编号": "0127",
      "备注": "0612 女 看起来五六十岁 更喜欢清静 刚刚好\n[identity repair 2026-06-14] 0612 女 看起来五六十岁 更喜欢清静 刚刚好",
      "年龄段": "50~59",
      "性别": "女",
      "教育层级": "本科",
      "更新时间": 1781323649000,
      "本地参与者ID": "18",
      "本地用户ID": "18",
      "登记姓名": "20260612-1",
      "研究阶段": "未填写",
      "诊断大类": "其他/未填写"
    }
  },
  {
    "record_id": "recvmkN4nwjW3a",
    "participant_code": "0128",
    "registered_name": "20260612-2",
    "registered_name_key": "20260612-2",
    "gender": "女",
    "user_id": "19",
    "local_id": "19",
    "updated_at": 1781249316000,
    "raw_fields": {
      "创建时间": 1781249307000,
      "参与者编号": "0128",
      "备注": "[identity repair 2026-06-14] 三处花朵；0612 女 白头发 70 及以上 喜欢热闹 桌椅 树木 花朵 与个人经历相关（父亲 花园工作）",
      "年龄段": "60~69",
      "性别": "女",
      "教育层级": "未填写",
      "更新时间": 1781249316000,
      "本地参与者ID": "19",
      "本地用户ID": "19",
      "登记姓名": "20260612-2",
      "研究阶段": "未填写",
      "诊断大类": "其他/未填写"
    }
  }
]
```

### Feishu Duplicate Name+Gender

```json
[]
```

### Feishu Missing Identity Fields

```json
[]
```

## Downstream Tables

### `session_summary`

- Table: `tblJ8uNrq1VbskhJ`
- Records: `1`
- Duplicate unique values: `0`
- Identity mismatches: `0`
- Target records: `1`

```json
{
  "target_records": [
    {
      "record_id": "recvmoArUYkQRe",
      "unique_value": "3c8a18bb9b2b",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    }
  ],
  "identity_mismatches": []
}
```

### `drag_element_summary`

- Table: `tbl5rKD7pngR3JPT`
- Records: `10`
- Duplicate unique values: `0`
- Identity mismatches: `0`
- Target records: `5`

```json
{
  "target_records": [
    {
      "record_id": "recvlKzqSllVDD",
      "unique_value": "3df68d9b2663",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    },
    {
      "record_id": "recvmcH8g6XQ3i",
      "unique_value": "7deacd798d89",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    },
    {
      "record_id": "recvmiNfLAPpfo",
      "unique_value": "c9a8261e3962",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    },
    {
      "record_id": "recvmjqAlv7Ntt",
      "unique_value": "34dafa28e4e8",
      "participant_code": "0127",
      "display_name": "20260612-1",
      "display_name_key": "20260612-1"
    },
    {
      "record_id": "recvmkN3nyOHlL",
      "unique_value": "abb35fe9eb0d",
      "participant_code": "0128",
      "display_name": "20260612-2",
      "display_name_key": "20260612-2"
    }
  ],
  "identity_mismatches": []
}
```

### `inspire_element_summary`

- Table: `tblRHCZlil3gxHJP`
- Records: `9`
- Duplicate unique values: `0`
- Identity mismatches: `0`
- Target records: `5`

```json
{
  "target_records": [
    {
      "record_id": "recvmcFqJSK0m9",
      "unique_value": "31b9a4b618b9",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    },
    {
      "record_id": "recvmcHGJyycBZ",
      "unique_value": "3df68d9b2663",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    },
    {
      "record_id": "recvmiOC7lnHy3",
      "unique_value": "732b951723f0",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    },
    {
      "record_id": "recvmiSJ8NGsDp",
      "unique_value": "6c102ce49620",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    },
    {
      "record_id": "recvmjqBxqSRSs",
      "unique_value": "c02047060de3",
      "participant_code": "0127",
      "display_name": "20260612-1",
      "display_name_key": "20260612-1"
    }
  ],
  "identity_mismatches": []
}
```

### `chat_mode_summary`

- Table: `tblZkSIqni3IjZ9J`
- Records: `22`
- Duplicate unique values: `0`
- Identity mismatches: `0`
- Target records: `2`

```json
{
  "target_records": [
    {
      "record_id": "recvmfKYb5q2I2",
      "unique_value": "1edaf6b5fcf7",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    },
    {
      "record_id": "recvmfKYb5Xw6q",
      "unique_value": "def9692f8289",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    }
  ],
  "identity_mismatches": []
}
```

### `slider_mode_summary`

- Table: `tbl0b7OU7sommUqK`
- Records: `12`
- Duplicate unique values: `0`
- Identity mismatches: `0`
- Target records: `2`

```json
{
  "target_records": [
    {
      "record_id": "recvmoyL8dmG36",
      "unique_value": "c5918f359480",
      "participant_code": "0127",
      "display_name": "20260612-1",
      "display_name_key": "20260612-1"
    },
    {
      "record_id": "recvmoyL8dRifZ",
      "unique_value": "3ac341d0b345",
      "participant_code": "0128",
      "display_name": "20260612-2",
      "display_name_key": "20260612-2"
    }
  ],
  "identity_mismatches": []
}
```

### `mode_usage_count`

- Table: `tblswhN4OsyWRZwj`
- Records: `11`
- Duplicate unique values: `0`
- Identity mismatches: `0`
- Target records: `3`

```json
{
  "target_records": [
    {
      "record_id": "recvmq5nC5kKgl",
      "unique_value": "0128",
      "participant_code": "0128",
      "display_name": "20260612-2",
      "display_name_key": "20260612-2"
    },
    {
      "record_id": "recvmq5nC5Plze",
      "unique_value": "0127",
      "participant_code": "0127",
      "display_name": "20260612-1",
      "display_name_key": "20260612-1"
    },
    {
      "record_id": "recvmq5nC5jW77",
      "unique_value": "0124",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    }
  ],
  "identity_mismatches": []
}
```

### `work_count_summary`

- Table: `tblsa0bsFu7I1tHs`
- Records: `12`
- Duplicate unique values: `0`
- Identity mismatches: `0`
- Target records: `3`

```json
{
  "target_records": [
    {
      "record_id": "recvmq5ozIO4z4",
      "unique_value": "0128",
      "participant_code": "0128",
      "display_name": "20260612-2",
      "display_name_key": "20260612-2"
    },
    {
      "record_id": "recvmq5ozIsFR8",
      "unique_value": "0127",
      "participant_code": "0127",
      "display_name": "20260612-1",
      "display_name_key": "20260612-1"
    },
    {
      "record_id": "recvmq5ozIKG8B",
      "unique_value": "0124",
      "participant_code": "0002",
      "display_name": "Arya",
      "display_name_key": "arya"
    }
  ],
  "identity_mismatches": []
}
```

## Machine Summary

- Total local duplicate groups: `2`
- Total Feishu participant duplicate groups: `0`
