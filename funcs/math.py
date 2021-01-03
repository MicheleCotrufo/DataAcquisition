#This module contains several functions which are used to parse and evaluate mathematical expressions for user-defined post-processed data

def CheckListIsValidFormula(List,ValidVariableNames):
    flag = 1
    msg = ''
    for elem in List:
        if type(elem) == str:
            if not ((elem in ValidVariableNames) or (elem in ['+','-','*','/'])):
                flag = 0
                msg = "One of the elements ('" + elem + "') of the list is neither a valid data name (in the format Dev#_DataName) nor a valid mathematical operation ('+', '-', '*', '/')"
                break
        elif isinstance(elem, list):
            msg, flag = CheckListIsValidFormula(elem,ValidVariableNames)
        else:
            flag = 0
            msg = 'One of the elements of the list is neither a string nor a list'
            break
    return msg, flag


def EvaluateFormula(Formula,Variables):
    #Formula is structured list
    #Variabes is a dictionary of "NameVariable":ValueVariable
    Value = 0
    operation = '+'
    for elem in Formula:
        if elem in ['+','-','*','/']:
            operation = elem
        else: 
            if isinstance(elem, list):
                NewValue = EvaluateFormula(elem,Variables)
            else:
                NewValue =  Variables[elem]
            Value = Operation(Value,NewValue,operation)
    return Value

def Operation(Value1,Value2,Operation):
    if Operation == '+':
        Value = Value1 + Value2
    if Operation == '*':
        Value = Value1 * Value2
    if Operation == '-':
        Value = Value1 - Value2
    if Operation == '/':
        try:
            Value = Value1 / Value2
        except ZeroDivisionError:
            Value = float('nan') 
    return Value


## TESTS

#Formula = ['a','/',['b','+','c']]
#ValidVariableNames = ['a','b']
#msg,flag=CheckListIsValidFormula(Formula ,ValidVariableNames)
#Variables = {'a':1,'b':1,'c':2}

#value = EvaluateFormula(Formula,Variables)
#print(value)
