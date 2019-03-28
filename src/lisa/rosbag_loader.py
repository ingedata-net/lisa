
def load(filename):
  with rosbag.Bag(filename) as bag:
    for topic, msg, t in bag.read_messages():
      print(msg)

if __name__ == "__main__":
    load("sample/ros.bag")