# -*- coding: utf-8 -*-

'''Example module.

This module defines Example class.
Created on 2019/12/08


Copyright ycookjp
https://github.com/ycookjp/

'''

class MyClass(object):
    '''Example class.
    
    Coding style, comment , etc examples.
    '''


    def __init__(self, param1):
        '''Constructor.
        
        Construct MyClass.
        
        :param: param1: parameter one
        '''
        
        
    publicAttribute = 'default value'
    '''This is a public attribute.'''
    
    
    _priateAttribute = 'default value'
    '''This is a private attribute.'''
    
    
    def publicMethod(self, arg1):
        '''Public method.
        
        This is a public method.
        
        :param: arg1: public method arg1
        :return: returns arg1.
        '''
        
        pass
        return arg1
    
    def _privateMethod(self, arg1):
        '''Private method.
        
        This is a private method.
        
        :param: arg1: private method arg1
        :return: returns arg1.
        '''
        
        pass
        return arg1
    