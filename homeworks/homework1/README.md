# Домашно 1

В лабораторията си за изкуствен интелект, младият Декстър се опитва да създаде първия си AI агент. Понеже той не беше посетил събитието на PyData София, той няма идея как да направи своя агент, и се нуждае от вашата помощ !

## Клас `LLM`

Първата стъпка към създаването на AI агент е моделът - в нашия случай, при създаването на модел ще подаваме списък с жетони (или по-правилното му наименование, tokens). Класът `LLM` ще играе ролята и на итератор.

```python
tokens = [
    "<response>",
    "Hello",
    "there",
    "</response>",
]

model = LLM(tokens)

for token in model:
    print(token)  # Prints "<response>"", then "Hello", etc.
```

Резултатът от модела е в следният формат:

- Всеки отговор започва с `<response>` и завършва с `</response>`.
- В отговора може да имаме обикновени token-и.
- Извикване на tool започва с `<tool_call>` и завършва с `</tool_call>`.
    - След започнат tool call, името на tool-а ще е обграден с `<name>` и `</name>`
    - След името, следват аргументите (`<arguments>`, `</arguments>`). Аргументите не са задължителни - tool може да бъде извикан и без тях.
    - Аргументите се отнасят само за текущото извикване - всяко ново извикване на tool започва без аргументи.
- Имаме и специални `<memory>` и `</memory>` тагове, между които е едно число.
- След затварящ таг (`</tool_call>`, `</memory>`) следващите token-и се обработват нормално.
- Таговете `<name>`, `</name>`, `<arguments>` и `</arguments>` имат специално значение само в рамките на tool call. Извън tool call те (и token-ите между тях) са обикновени token-и.

Пример:

```
<response>
Hello
there
</response>
<response>
2
+
2
is
<tool_call>
<name>
concat
</name>
<arguments>
2
3
4
</arguments>
</tool_call>
</response>
<response>
<tool_call>
<name>
ask_user
</name>
</tool_call>
Hello,
<memory>
0
</memory>
</response>
```

## Клас `ToolRegistry`

Освен модел, агентът се нуждае и от инструменти (или по-правилното им наименувание, tools).

Класът има три метода:

- `register` - приема `tool_name` и `tool_action` (функция, която приема произволен брой низове и връща резултат).
- `is_available` - проверява дали даден tool съществува.
- `execute` - изпълнява tool с име `tool_name`, като подава всички останали аргументи към функцията. Връща резултатът от нея. Ако такъв tool липсва, връща None.

```python

def some_random_tool(a):
    return 42 + int(a)

tool_registry = ToolRegistry()
tool_registry.register("some_random_tool", some_random_tool)

tool_registry.is_available("some_random_tool")  # True
tool_registry.is_available("other_random_tool")  # False

tool_registry.execute("some_random_tool", "45")  # 87
```

Инструментите, които ще дадем на нашия агент са:

- `add` - връща сумата на всички подадени числа (като число).
- `concat` - конкатенира всички подадени низове.
- `ask_user` - прочита съобщение от клавиатурата.

## Клас `Agent`

Агентът ни приема модел и инструменти. Неговият единствен метод `run` е генератор, и обработва token-ите получени от модела, като:

- При начало на отговор започваме да броим изполваните token-и (в кредити) от 0.
- В края на отговора, връщаме празен низ, и броя използвани кредити за текущия отговор.
- При tool call, извикваме съответния tool с аргументите, подадени в рамките на същия tool call, и връщаме резултата. Ако такъв tool не съществува, връщаме "Invalid tool name.". Извикване на tool винаги струва 2 кредита (дори и ако не открием tool).
- Ако извикаме tool `ask_user`, прочетеното съобщение записваме в паметта на модела (списък от низове). Това струва 3 кредита (общо).
- При тагове `<memory>` прочитаме стойност от паметта (числото между таговете е индекс в паметта, започващ от 0) и я връщаме. Това не струва кредити.
- Във всички други ситуации, връщаме директно token-а. Тази операция струва 1 кредит.

## Декоратор `observe`

Понякога е добре да знаем какво ни е върнал модела, и какво е направил нашия агент. Дефинирайте декоратор `observe`, който ще декорира нашия модел - при "генерирането" на token, `observe` първо го принтира по следния начин: "DEBUG: Next token is <token>", където `<token>` е token-а генериран от модела.


## Очаквана структура

При разархивиране на домашното, трябва да бъде получена следната структура:

```bash
agent.py
```

## Пример

```python
tokens = [
    "<response>", "Hello", "there", "</response>",
]
tokens += [
    "<response>", 
    "2", "+", "2", "is",
    "<tool_call>", 
    "<name>", "concat", "</name>",
    "<arguments>", "2", "3", "4", "</arguments>",
    "</tool_call>",
    "</response>",
]

tokens += [
    "<response>",
    "<tool_call>",
    "<name>", "ask_user", "</name>",
    "</tool_call>",
    "Hello,", "<memory>", "0", "</memory>",
    "</response>",
]

model = LLM(tokens)

tool_registry = ToolRegistry()
tool_registry.register("add", add)
tool_registry.register("concat", concat)
tool_registry.register("ask_user", ask_user)

agent = Agent(model, tool_registry)

for result in agent.run():
    if isinstance(result, tuple):
        print(result[0])
        print(f"(Usage: {result[1]} tokens)")
    else:
        print(result, end=" ")
```

```bash
$ python3 agent.py
Hello there
(Usage: 2 tokens)
2 + 2 is 234
(Usage: 6 tokens)
Lyubo
Hello, Lyubo
(Usage: 4 tokens)
```