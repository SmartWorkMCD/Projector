# import paho.mqtt.publish as publish
# import json

# message = json.dumps({
#     "task": "Assemble",
#     "subtask": "ScrewBolt",
#     "progress": 85,
#     "state": {
#         "CombinationValid": True,
#         "HandGridCell": "C3"
#     }
# })

# publish.single("test", payload=message, hostname="localhost", port=1883)

import json, time
import paho.mqtt.publish as publish


# simulated data
task_name = "Montar sapato"
subtask_name = "Produto 1: 4 azuis, 2 amarelos e 3 verdes"
action1 = "highlight-green" # action-color
action2 = "highlight-red" # action-color
cell = "C5"
progress = "35" # progress percentage

action = None
for i in range(0,4):

    if (action is None or action==action1):
        action = action2
    else:
        action = action1

    # final message structure
    message = json.dumps({
        "task": task_name,
        "subtask": subtask_name,
        "action": action,
        "cell": cell,
        "progress": progress
    })

    message2 = json.dumps({
        "task": task_name,
        "subtask": subtask_name,
        "action": action2,
        "cell": cell,
        "progress": progress
    })

    # send via MQTT
    try:
        publish.single("test", payload=message, hostname="localhost", port=1883)
        print("[MQTT] Message published successfully")
        print(message)
    except Exception as e:
        print(f"[Erro MQTT] {e}")

    time.sleep(15)  # simulate delay between message