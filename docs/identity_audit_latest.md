# Identity Audit Report

- Generated at: `2026-06-14T00:29:06`
- Local DB: `D:\SSH\环境游戏程序\healing-environment\data\healing.db`
- Feishu enabled: `True`

## Local Summary

- Users: `11`
- HCI participants: `6`
- Sessions: `715`
- Duplicate user name+gender groups: `1`
- Duplicate participant name+gender groups: `0`
- Mismatched user/participant codes: `1`
- Users without HCI participant row: `5`

### Local Target Participants

```json
[
  {
    "id": 5,
    "user_id": 8,
    "participant_code": "0002",
    "registered_name": "Arya",
    "gender": "女",
    "created_at": 1780583531.921693,
    "updated_at": 1781236475.3108063,
    "participant_code_normalized": "0002",
    "registered_name_key": "arya"
  }
]
```

## Feishu Summary

- Participant table: `tblOpqLdd7QB9GCS`
- Participant records: `20`
- Duplicate name groups: `5`
- Duplicate name+gender groups: `3`
- Duplicate code groups: `2`
- Missing identity rows: `4`

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
    "record_id": "recvmf6LSaWLvN",
    "participant_code": "0124",
    "registered_name": "Arya",
    "registered_name_key": "arya",
    "gender": "女",
    "user_id": "7",
    "local_id": "1",
    "updated_at": 1781239935000,
    "raw_fields": {
      "创建时间": 1781185481000,
      "参与者编号": "0124",
      "年龄段": "18~29",
      "性别": "女",
      "教育层级": "未填写",
      "更新时间": 1781239935000,
      "本地参与者ID": "1",
      "本地用户ID": "7",
      "登记姓名": "Arya",
      "研究阶段": "未填写",
      "诊断大类": "其他/未填写"
    }
  },
  {
    "record_id": "recvmj3nFumCPD",
    "participant_code": "0125",
    "registered_name": "20260612-1",
    "registered_name_key": "20260612-1",
    "gender": "女",
    "user_id": "8",
    "local_id": "2",
    "updated_at": 1781243778000,
    "raw_fields": {
      "创建时间": 1781243778000,
      "参与者编号": "0125",
      "性别": "女",
      "更新时间": 1781243778000,
      "本地参与者ID": "2",
      "本地用户ID": "8",
      "登记姓名": "20260612-1"
    }
  },
  {
    "record_id": "recvmj3rIxfuJV",
    "participant_code": "0126",
    "registered_name": "Arya",
    "registered_name_key": "arya",
    "gender": "女",
    "user_id": "9",
    "local_id": "3",
    "updated_at": 1781243794000,
    "raw_fields": {
      "创建时间": 1781243794000,
      "参与者编号": "0126",
      "性别": "女",
      "更新时间": 1781243794000,
      "本地参与者ID": "3",
      "本地用户ID": "9",
      "登记姓名": "Arya"
    }
  },
  {
    "record_id": "recvmj3AZ8ZEJx",
    "participant_code": "0127",
    "registered_name": "20260612-1",
    "registered_name_key": "20260612-1",
    "gender": "其他/未填写",
    "user_id": "10",
    "local_id": "4",
    "updated_at": 1781323649000,
    "raw_fields": {
      "中心编号": "浦江",
      "创建时间": 1781243829000,
      "参与者编号": "0127",
      "备注": "0612 女 看起来五六十岁 更喜欢清静 刚刚好",
      "年龄段": "50~59",
      "性别": "其他/未填写",
      "教育层级": "本科",
      "更新时间": 1781323649000,
      "本地参与者ID": "4",
      "本地用户ID": "10",
      "登记姓名": "20260612-1",
      "研究阶段": "未填写",
      "诊断大类": "其他/未填写"
    }
  },
  {
    "record_id": "recvmk08Cu5qXs",
    "participant_code": "",
    "registered_name": "20260612-2",
    "registered_name_key": "20260612-2",
    "gender": "",
    "user_id": "",
    "local_id": "",
    "updated_at": null,
    "raw_fields": {
      "备注": "0612 女 白头发 70 及以上 喜欢热闹 桌椅 树木 花朵 与个人经历相关（父亲 花园工作）",
      "登记姓名": "20260612-2"
    }
  },
  {
    "record_id": "recvmkN4nwjW3a",
    "participant_code": "0128",
    "registered_name": "20260612-2",
    "registered_name_key": "20260612-2",
    "gender": "女",
    "user_id": "11",
    "local_id": "5",
    "updated_at": 1781249316000,
    "raw_fields": {
      "创建时间": 1781249307000,
      "参与者编号": "0128",
      "年龄段": "60~69",
      "性别": "女",
      "教育层级": "未填写",
      "更新时间": 1781249316000,
      "本地参与者ID": "5",
      "本地用户ID": "11",
      "登记姓名": "20260612-2",
      "研究阶段": "未填写",
      "诊断大类": "其他/未填写"
    }
  }
]
```

### Feishu Duplicate Name+Gender

```json
[
  {
    "key": {
      "registered_name_key": "arya",
      "gender": "女"
    },
    "items": [
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
        "record_id": "recvmf6LSaWLvN",
        "participant_code": "0124",
        "registered_name": "Arya",
        "registered_name_key": "arya",
        "gender": "女",
        "user_id": "7",
        "local_id": "1",
        "updated_at": 1781239935000,
        "raw_fields": {
          "创建时间": 1781185481000,
          "参与者编号": "0124",
          "年龄段": "18~29",
          "性别": "女",
          "教育层级": "未填写",
          "更新时间": 1781239935000,
          "本地参与者ID": "1",
          "本地用户ID": "7",
          "登记姓名": "Arya",
          "研究阶段": "未填写",
          "诊断大类": "其他/未填写"
        }
      },
      {
        "record_id": "recvmj3rIxfuJV",
        "participant_code": "0126",
        "registered_name": "Arya",
        "registered_name_key": "arya",
        "gender": "女",
        "user_id": "9",
        "local_id": "3",
        "updated_at": 1781243794000,
        "raw_fields": {
          "创建时间": 1781243794000,
          "参与者编号": "0126",
          "性别": "女",
          "更新时间": 1781243794000,
          "本地参与者ID": "3",
          "本地用户ID": "9",
          "登记姓名": "Arya"
        }
      }
    ]
  },
  {
    "key": {
      "registered_name_key": "codex虚拟测试06112308",
      "gender": "其他/未填写"
    },
    "items": [
      {
        "record_id": "recvmfsOrLh7VK",
        "participant_code": "0004",
        "registered_name": "Codex虚拟测试06112308",
        "registered_name_key": "codex虚拟测试06112308",
        "gender": "其他/未填写",
        "user_id": "10",
        "local_id": "8",
        "updated_at": 1781190650000,
        "raw_fields": {
          "中心编号": "TEST-CODEX",
          "创建时间": 1781190534000,
          "参与者编号": "0004",
          "性别": "其他/未填写",
          "教育层级": "未填写",
          "更新时间": 1781190650000,
          "本地参与者ID": "8",
          "本地用户ID": "10",
          "登记姓名": "Codex虚拟测试06112308",
          "研究阶段": "未填写",
          "诊断大类": "其他/未填写"
        }
      },
      {
        "record_id": "recvmfsOrLYTEZ",
        "participant_code": "0004",
        "registered_name": "Codex虚拟测试06112308",
        "registered_name_key": "codex虚拟测试06112308",
        "gender": "其他/未填写",
        "user_id": "10",
        "local_id": "8",
        "updated_at": 1781190650000,
        "raw_fields": {
          "中心编号": "TEST-CODEX",
          "创建时间": 1781190534000,
          "参与者编号": "0004",
          "性别": "其他/未填写",
          "教育层级": "未填写",
          "更新时间": 1781190650000,
          "本地参与者ID": "8",
          "本地用户ID": "10",
          "登记姓名": "Codex虚拟测试06112308",
          "研究阶段": "未填写",
          "诊断大类": "其他/未填写"
        }
      }
    ]
  },
  {
    "key": {
      "registered_name_key": "ipad-debug-1781238168711",
      "gender": "其他/未填写"
    },
    "items": [
      {
        "record_id": "recvmiTqwFmp3E",
        "participant_code": "0005",
        "registered_name": "ipad-debug-1781238168711",
        "registered_name_key": "ipad-debug-1781238168711",
        "gender": "其他/未填写",
        "user_id": "11",
        "local_id": "11",
        "updated_at": 1781238169000,
        "raw_fields": {
          "创建时间": 1781238169000,
          "参与者编号": "0005",
          "性别": "其他/未填写",
          "更新时间": 1781238169000,
          "本地参与者ID": "11",
          "本地用户ID": "11",
          "登记姓名": "ipad-debug-1781238168711"
        }
      },
      {
        "record_id": "recvmiTqwXi9bN",
        "participant_code": "0005",
        "registered_name": "ipad-debug-1781238168711",
        "registered_name_key": "ipad-debug-1781238168711",
        "gender": "其他/未填写",
        "user_id": "11",
        "local_id": "11",
        "updated_at": 1781238169000,
        "raw_fields": {
          "创建时间": 1781238169000,
          "参与者编号": "0005",
          "性别": "其他/未填写",
          "更新时间": 1781238169000,
          "本地参与者ID": "11",
          "本地用户ID": "11",
          "登记姓名": "ipad-debug-1781238168711"
        }
      }
    ]
  }
]
```

### Feishu Missing Identity Fields

```json
[
  {
    "record_id": "recvmf8K3z7cjc",
    "participant_code": "",
    "registered_name": "",
    "registered_name_key": "",
    "gender": "",
    "user_id": "",
    "local_id": "",
    "updated_at": null,
    "raw_fields": {}
  },
  {
    "record_id": "recvmfv25NSWmK",
    "participant_code": "",
    "registered_name": "",
    "registered_name_key": "",
    "gender": "",
    "user_id": "",
    "local_id": "",
    "updated_at": null,
    "raw_fields": {}
  },
  {
    "record_id": "recvmk08Cu5qXs",
    "participant_code": "",
    "registered_name": "20260612-2",
    "registered_name_key": "20260612-2",
    "gender": "",
    "user_id": "",
    "local_id": "",
    "updated_at": null,
    "raw_fields": {
      "备注": "0612 女 白头发 70 及以上 喜欢热闹 桌椅 树木 花朵 与个人经历相关（父亲 花园工作）",
      "登记姓名": "20260612-2"
    }
  },
  {
    "record_id": "recvmk0o8WAoGf",
    "participant_code": "",
    "registered_name": "",
    "registered_name_key": "",
    "gender": "",
    "user_id": "",
    "local_id": "",
    "updated_at": null,
    "raw_fields": {}
  }
]
```

## Downstream Tables

### `session_summary`

- Table: `tblDQueP2IcUENC8`
- Error: `Feishu API error 1254041: TableIdNotFound`

### `drag_element_summary`

- Table: `tbl5rKD7pngR3JPT`
- Records: `10`
- Duplicate unique values: `0`
- Identity mismatches: `3`
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
      "participant_code": "0124",
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
  "identity_mismatches": [
    {
      "record_id": "recvlAoOiSMpZ9",
      "unique_value": "4448bb7bc544",
      "participant_code": "U93667270",
      "display_name": "用户9366",
      "display_name_key": "用户9366",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmcF9iXiQoW",
      "unique_value": "d4674bbf4d9a",
      "participant_code": "",
      "display_name": "",
      "display_name_key": "",
      "issue": "missing_participant_code"
    },
    {
      "record_id": "recvmcF9iX8QKS",
      "unique_value": "0cbd3f4d319e",
      "participant_code": "",
      "display_name": "",
      "display_name_key": "",
      "issue": "missing_participant_code"
    }
  ]
}
```

### `inspire_element_summary`

- Table: `tblRHCZlil3gxHJP`
- Records: `9`
- Duplicate unique values: `0`
- Identity mismatches: `1`
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
      "participant_code": "0124",
      "display_name": "Arya",
      "display_name_key": "arya"
    },
    {
      "record_id": "recvmiSJ8NGsDp",
      "unique_value": "6c102ce49620",
      "participant_code": "0124",
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
  "identity_mismatches": [
    {
      "record_id": "recvlABRo9RsH6",
      "unique_value": "82fb0696261a",
      "participant_code": "U93667270",
      "display_name": "用户9366",
      "display_name_key": "用户9366",
      "issue": "code_not_in_participant_table"
    }
  ]
}
```

### `chat_mode_summary`

- Table: `tblZkSIqni3IjZ9J`
- Records: `22`
- Duplicate unique values: `0`
- Identity mismatches: `5`
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
  "identity_mismatches": [
    {
      "record_id": "recvmfKYb5WJhU",
      "unique_value": "0c0fb222d460",
      "participant_code": "0123",
      "display_name": "123",
      "display_name_key": "123",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmfKYb5VHrw",
      "unique_value": "3ab807fc377e",
      "participant_code": "0123",
      "display_name": "123",
      "display_name_key": "123",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmfKYb54ET7",
      "unique_value": "6114860e0902",
      "participant_code": "0123",
      "display_name": "123",
      "display_name_key": "123",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmfKYb5dZoz",
      "unique_value": "98808ba793ef",
      "participant_code": "0123",
      "display_name": "123",
      "display_name_key": "123",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmfKYb5tGVn",
      "unique_value": "ef7a1bba952b",
      "participant_code": "0111",
      "display_name": "111",
      "display_name_key": "111",
      "issue": "code_not_in_participant_table"
    }
  ]
}
```

### `slider_mode_summary`

- Table: `tbl0b7OU7sommUqK`
- Records: `12`
- Duplicate unique values: `0`
- Identity mismatches: `2`
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
  "identity_mismatches": [
    {
      "record_id": "recvmfLfv9gWnO",
      "unique_value": "0fd80d0eb0b5",
      "participant_code": "0111",
      "display_name": "111",
      "display_name_key": "111",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmfLfv91FvS",
      "unique_value": "62b45b710da5",
      "participant_code": "0123",
      "display_name": "123",
      "display_name_key": "123",
      "issue": "code_not_in_participant_table"
    }
  ]
}
```

### `mode_usage_count`

- Table: `tblswhN4OsyWRZwj`
- Records: `11`
- Duplicate unique values: `0`
- Identity mismatches: `6`
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
      "participant_code": "0124",
      "display_name": "Arya",
      "display_name_key": "arya"
    }
  ],
  "identity_mismatches": [
    {
      "record_id": "recvmq5nC5IVPh",
      "unique_value": "U93667270",
      "participant_code": "U93667270",
      "display_name": "用户9366",
      "display_name_key": "用户9366",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmq5nC51kdo",
      "unique_value": "P001",
      "participant_code": "P001",
      "display_name": "你好",
      "display_name_key": "你好",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmq5nC5hcd9",
      "unique_value": "0001",
      "participant_code": "0001",
      "display_name": "1",
      "display_name_key": "1",
      "issue": "code_name_mismatch"
    },
    {
      "record_id": "recvmq5nC5JXOJ",
      "unique_value": "P002",
      "participant_code": "P002",
      "display_name": "你好",
      "display_name_key": "你好",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmq5nC5ow0r",
      "unique_value": "0123",
      "participant_code": "0123",
      "display_name": "123",
      "display_name_key": "123",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmq5nC5zyp8",
      "unique_value": "0111",
      "participant_code": "0111",
      "display_name": "111",
      "display_name_key": "111",
      "issue": "code_not_in_participant_table"
    }
  ]
}
```

### `work_count_summary`

- Table: `tblsa0bsFu7I1tHs`
- Records: `12`
- Duplicate unique values: `0`
- Identity mismatches: `6`
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
      "participant_code": "0124",
      "display_name": "Arya",
      "display_name_key": "arya"
    }
  ],
  "identity_mismatches": [
    {
      "record_id": "recvmq5ozImQBG",
      "unique_value": "U93667270",
      "participant_code": "U93667270",
      "display_name": "用户9366",
      "display_name_key": "用户9366",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmq5ozIXab8",
      "unique_value": "P001",
      "participant_code": "P001",
      "display_name": "你好",
      "display_name_key": "你好",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmq5ozIxo4x",
      "unique_value": "0001",
      "participant_code": "0001",
      "display_name": "1",
      "display_name_key": "1",
      "issue": "code_name_mismatch"
    },
    {
      "record_id": "recvmq5ozI1PqY",
      "unique_value": "P002",
      "participant_code": "P002",
      "display_name": "你好",
      "display_name_key": "你好",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmq5ozImPvy",
      "unique_value": "0123",
      "participant_code": "0123",
      "display_name": "123",
      "display_name_key": "123",
      "issue": "code_not_in_participant_table"
    },
    {
      "record_id": "recvmq5ozILsN6",
      "unique_value": "0111",
      "participant_code": "0111",
      "display_name": "111",
      "display_name_key": "111",
      "issue": "code_not_in_participant_table"
    }
  ]
}
```

## Machine Summary

- Total local duplicate groups: `2`
- Total Feishu participant duplicate groups: `19`
