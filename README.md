# brackstack
Utility script that displays the contents of nested brackets on seperate lines. Used to make code with multiple levels of nesting more readable by adding a vertical dimension.

## Todo

* add examples
* possibly add ahkscript to bind the script to a hotkey

## Examples

### Finding a missing closing bracket

#### Input

The following line of code is missing a right paren. 

    a = [foo(dict(bar=3,car='zar')]

#### Output

![Example missing closing bracket](http://i.imgur.com/LpaCWNF.png)




#### Input

    )a(a)(b[c]],{sum(range(max(array([1,2,3],[4,5,5]))))})

#### Output

![snapshot1](http://i.imgur.com/kWkJ1Yt.png)

