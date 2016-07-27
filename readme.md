此项目只是用于测试从外部调用ansible的可能性.

测试的时候请上传真是的``ctgmq-rocketmq-2.0.3.P2-ctgmq-rocketmq.tar.gz``
测试命令行

```BASH
itsm-ansible  -i "{
  \"host_roles\": [
    {
      \"hosts\": \"all\",
      \"roles\": [
        {
          \"role\": \"common\",
          \"vars\": {}
        }
      ]
    },
    {
      \"hosts\": \"rocketmq-nameservers\",
      \"roles\": [
        {
          \"role\": \"rocketmq-nameserver\",
          \"vars\": {}
        }
      ]
    },
    {
      \"hosts\": \"rocketmq-brokers\",
      \"roles\": [
        {
          \"role\": \"rocketmq-broker\",
          \"vars\": {}
        }
      ]
    }
  ],
  \"hosts\": [
    {
      \"groups\": [
        \"rocketmq-nameservers\"
      ],
      \"host_vars\": {},
      \"hostname\": \"rocketmq-nameserver1\",
      \"ip\": \"117.121.26.152\",
      \"password\": \"Root.123\",
      \"port\": \"2002\",
      \"user\": \"root\"
    },
    {
      \"groups\": [
        \"rocketmq-brokers\"
      ],
      \"host_vars\": {
        \"brokerClusterName\": \"test_207_cluster\",
        \"brokerId\": \"1\",
        \"brokerName\": \"broker-c\",
        \"brokerRole\": \"SYNC_MASTER\",
        \"storeNodeName\": \"test_node_205_master\"
      },
      \"hostname\": \"rocketmq-broker1\",
      \"ip\": \"117.121.26.152\",
      \"password\": \"Root.123\",
      \"port\": \"2003\",
      \"user\": \"root\"
    }
  ],
  \"playbook\": \"/Users/jinlin/code/python/itsm_ansible/rocketmq\",
  \"task_id\": \"11111\"
}" -vvvvv
```

测试提交1

测试提交2 - 尝试两种merge方式

测试提交3.1 - 一下子提交两个commit 
测试提交3.2 - 一下子提交两个commit 

测试冲突
