class Node:
        def __init__(self,value):
            self.left = []
            self.value = value
            self.right = []

        def node_iterate(self):
            for value in self.child_iterate(self.left):
                v = yield value
                print('left v is %s' % v)
            v = yield self.value
            for value in self.child_iterate(self.right):
                s = yield value
                print('right v is %s' % s)

        def child_iterate(self,nodes):
            for node in nodes:
                input_value = yield node.value
                print('input value is %s' % input_value)

        def main():
            root = Node(0)
            root.left = [Node(i) for i in [1,2,3]]
            root.right = [Node(i) for i in [4,5,6]]
            it = root.node_iterate()
            total = it.send(None)
            while True:
                try:
                    ans = it.send(total)
                    total += ans
                except StopIteration:
                    break
                else:
                    print('ans is %s' % ans)
            print('total is %s' % total)
if __name__ == '__main__':
        Node.main()
