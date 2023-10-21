import requests
import unittest
from unittest.mock import patch

class MyClass():
    '''テスト対象のクラス
    '''
    def __init__(self):
        self.attr1 = None

    def doSomething(self, no: int):
        print(f'No.{no} Good morning.')

    def doAnother(self, no: int):
        print(f"No.{no} Good by.")

    def methodA(self, url):
        return self.methodB(url)
    
    def methodB(self, url):
        response = requests.get(url)
        result = response.text
        return result

class MyResponse():
    '''requests.Responseオブジェクトの代わりに使用するオブジェクト
    '''    
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

def mock_get(url) :
    '''request.get メソッドの代わりに使用するメソッド
    urlの最後の「/」とその前の「/」との間の文字列が「func1」の場合は、
    「200: Success.」を返し、それ以外の場合は「404: Error.」を返す。
    '''
    items = url.split('/')
    action = items[len(items) - 2]
    if action == 'func1':
        return MyResponse(200, 'Success.')
    else:
        return MyResponse(404, 'Error.')

class TestMyClass(unittest.TestCase):
    def testAccess(self):
        '''MyClassの属性、メソッドの呼び出し確認をする
        MyClass の属性やメソッドが正しい引数で呼び出されたことをテストする。
        '''
        with patch('MockTest.MyClass') as mock:
            # MyClass のインスタンスを Mock オブジェクトから取得する
            instance = mock.return_value
            # nyClass(実はMockオブジェクト)のメソッド、属性にアクセスする
            instance.doSomething(1)
            instance.doAnother(2)
            instance.attr1 = 3

            # MyClass の doSomething メソッドが引数「1」を指定して呼び出された
            # ことを確認する
            instance.doSomething.assert_called_with(1)
            # MyClass の doAnother メソッドが引数「2」を指定して呼び出された
            # ことを確認する
            instance.doAnother.assert_called_with(2)

    def testMethodA(self):
        '''MyClass の methodA のテストを実行する
        methodBの内部で request.get により呼び出している Web API を実行できない
        ので、methodB が 'Hello world.' が返すことにしてテストを実行する。
        '''
        instance = MyClass()
        # オブジェクト(MyClass)の methodB を Mock オブジェクトに置換し、
        # 置換されたMock オブジェクトの return_value に 'Hello world.' を設定
        with patch.object(MyClass, 'methodB', return_value='Hello world.'):
            result = instance.methodA('http://www.foo.bar.xyz/func1/')
            self.assertEqual(result, 'Hello world.')

    def testMethodAMultiple(self):
        '''MyClass の methodA のテストを実行する
        methodBの内部で request.get により呼び出している Web API を実行できない
        ので、methodB が 'Hello world.' が返すことにしてテストを実行する。
        '''
        myClass = MyClass()
        # オブジェクト(MyClass)の methodB を Mock オブジェクトに置換し、
        # 置換されたMock オブジェクトの return_value に 'Hello world.' を設定
        with patch.object(MyClass, 'methodB',
                side_effect=['Hello world.', 'Good by.']):
            # methodA から medhodB への１回目の呼び出し
            result = myClass.methodA('http://www.foo.bar.xyz/func1/')
            self.assertEqual(result, 'Hello world.')
            
            # methodA から medhodB への２回目の呼び出し
            result = myClass.methodA('http://www.foo.bar.xyz/func1/')
            self.assertEqual(result, 'Good by.')

    def testMethodAMultiple(self):
        '''呼び出される度に戻り値が異なるメソッドをモックしてテストする
        methodBの内部で request.get により呼び出している Web API を実行できない
        ので、methodB が 'Hello world.'、'Good by.'を順に返すことにしてテストを
        実行する。
        '''
        myClass = MyClass()
        # オブジェクト(MyClass)の methodB を Mock オブジェクトに置換し、
        # 置換されたMock オブジェクトの return_value に 'Hello world.' を設定
        with patch.object(MyClass, 'methodB',
                side_effect=['Hello world.', 'Good by.']):
            # methodA から medhodB への１回目の呼び出し
            result = myClass.methodA('http://www.foo.bar.xyz/func1/')
            self.assertEqual(result, 'Hello world.')
            
            # methodA から medhodB への２回目の呼び出し
            result = myClass.methodA('http://www.foo.bar.xyz/func1/')
            self.assertEqual(result, 'Good by.')

    def testMethodBException(self):
        '''requests.get 関数の例外発生テストをする
        requests.get を実行したら ConnectionError が発生した場合のテストを
        実行する。
        '''
        myClass = MyClass()
        with patch('requests.get', side_effect=requests.ConnectionError):
            with self.assertRaises(requests.ConnectionError):
                myClass.methodB('http://www.foo.bar.xyz/func1/')

    def testMethodReplace(self):
        '''requests.getメソッドをテスト用のロジックに置き換えてテストする
        request.getメソッドで呼び出すWeb APIが実行できないので、テスト用の
        ロジックに置き換えてテストする。
        '''
        instance = MyClass()
        # requestsモジュールの get 関数を mock_get 関数に置き換える
        with patch('requests.get', side_effect=mock_get):
            response = instance.methodB('http://www.foo.bar.xyz/func1/')
            self.assertTrue(response, 'Success.')
            response = instance.methodB('http://www.foo.bar.xyz/func2/')
            self.assertTrue(response, 'Error.')
