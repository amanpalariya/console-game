# Console Game Language
You can use this language to create simple games that run on a simple retro console simulator.
It is recommended to use `.cg` as the file extension.

Jump to the **The Language** section to learn how to code in this language.
The `samples` directory contains a few sample code files, please try running them to understand the working.

## Technical details
The core implements a RegEx based lexical analyzer and an LR(0) parser.
The grammar is defined in a form similar to BNF.

## Project Structure
The compiler for the language is present in the `language` directory.
The `samples` directory contains some sample codes.

## How to run?

### Prerequisite
The simulator need [PyGame] 2.0+ to run.
It has been tested on Python 3.8.6.

Considering that you have the code written in the file `code.gb`, you can run the code by running the following command.

```
python3 language/runner.py code.gb
```

The above command will run the game on a 30×30 console at 30 frames per second.
To run with custom configuration (say 30×20 at 10 frames per second), use the following command

```
python3 language/runner.py code.gb 30 20 10
```

# Runtime Environment
The code is run on a retro console simulator made with [PyGame].

## Input
The console has 6 buttons - *Power*, *Start*, *X*, *Y*, *A*, and *B*.

| Button | Mapping |
| ------ | ------- |
| *Power*  | <kbd>Return</kbd> |
| *Start*  | <kbd>Space</kbd> |
| *X*      | <kbd>X</kbd> or <kbd>&larr;</kbd> |
| *Y*      | <kbd>Y</kbd> or <kbd>&uarr;</kbd> |
| *A*      | <kbd>A</kbd> or <kbd>&darr;</kbd> |
| *B*      | <kbd>B</kbd> or <kbd>&rarr;</kbd> |

The *Power* button is used to turn on/off the console. 
Other buttons work as defined in the code.

## Output
The console has a display - a grid of black and white pixels.
The language provides commands to display shapes on the screen.

## Processing
The console is driven by a clock whose frequency is decided during compile time.
At every tick, code corresponding to the current state is executed - computation, updating display, changing the state, etc.

> The games may run at different speed at different frequencies.

# The Language

## Basic concepts
The game is a state machine.
We can define states and jump from one to another. 
The console simulator has a clock which runs at a fixed speed (defaults to 30Hz).
At each tick, the operations defined within a state are executed and the state is updated as required.

## File structure
The first line of the file must be the name of the initial state.

## Comments
Anything followed by a `//` until the end of the line is considered a comment.
Comments cannot appear at the beginning of the file.
They must be present after initial state declaration.

## Shape
A shape is a 2D collection of pixel color (black, white, or transparent).
The shapes can be painted(overlaid) on a screen.

A shape can be defined as follows.
```
#disc {
..##..
.#++#.
#++++#
#++++#
.#++#.
..##..
}
```
Here, `#disc` is the name of the shape. `#` represents a black pixel, `+` represents a white pixel, and `.` represents a transparent pixel.

Shape name is a `#` followed by one or more alphanumeric or underscore character.

> Shapes can be defined only at the root of the document.

## State
A state is a collection of statements.
Variable assignment, button handling, state change, and display update statements can be written inside a state.

```c
~firstState{
  // Statements go here
}
```

Here, `~firstState` is the name of the state.

State name is a `~` followed by one or more alphanumeric or underscore character.

### Variable
Variables can store intergers only and are global in scope.
If not defined, variables default to 0.

Here is an example of variable assignment

```c
$four = [2+2]
```

Here, `$four` is the name of the variable.
After execution of the statement, 4 is stored in the variable `$four`.

Variable name is a `$` followed by one or more alphanumeric or underscore character.

### Constants
There are 3 constants present in the language.

| Constant | Meaning |
| -------- | ------- |
| `!W`     | The width of the device (default 30) |
| `!H`     | The height of the device (default 30) |
| `!FPS`   | The frame rate of the device (default 30) |

### Expression
An expression is used to do arithmetic or logical operations on literals, variables, or constants.

The code snippet below shows the use of expression.

```c
$a = [1+2]
$aSquaredMod10 = [($a*$a)%10]
```

The precedence of the operators are as follows (in descending order)

| Operator                        | Description |
| ------------------------------- | ----------- |
| `(`, `)`                        | Parentheses |
| `+`, `-`, `~`                   | Unary *plus*, *minus*, *not* |
| `*`, `/`, `%`                   | *Multiplication*, *integer division*, *modulo* |
| `+`, `-`                        | *Addition*, *subtraction* |
| `<=`, `<`, `>=`, `>`, `=`, `~=` | *Less than or equal to*, *less than*, *greater than or equal to*, *greater than*, *equal to*, *not equal to*|
| `&`, `\|`                       | Logical *and*, *or* |

The associativity for all operators is from left to right.

> The logical operators consider zero as `false` and non-zero values as `true`.
> The logical operators evaluate to 0 instead of `false` and 1 instead of `true`.

#### Random expression
Random numbers are important part of games.
We can generate random number as follows.

```c
$randomNumberOnADice = r[1][6] 
$randomNumberOnADice = r[6][1] // Same as previous statement

$anotherRandomNumber = r[0][!W-1]
```

> Random expression are also expressions.

### Selection
We can use `if` and `if not` to make selections.
Any expression can be used as a boolean expression.
Zero represents a `false` value and any non-zero value represents `true`.

```c
if [2+2=4]{
  // Statements
}

if not [$x>10]{
  // Statements
}
```

> The body of an `if` statement cannot be empty.
> There is no `else` statement present in the language.

### Iteration
The language provides `while` and `while not` for iterations.
In case of an infinite loop, the device freezes.

Here is an example
```c
$x = [0]
while [$x<5]{
  // Statements
  $x = [$x+1]
}
```

### Screen update
There are two commands for updating the screen - `clear` and `display`.

#### clear
Clears the whole screen. 

```
clear
```

#### display
It is used to overlay a shape on the screen.
The top-left coordinate of the position where the shape is to be overlayed are required.

```vim
display #someShape @ ([$x], [$y])
display #anotherShape @ ([!W - $x], [!H - $y])
```

The coordinates are two expressions.

### State change
At every tick, the code inside the current state is executed.
We can change the current state by using `goto` statement.

```c
goto ~anotherState
```

Any code following `goto` is not executed.

### Button handler
Button handlers are defined inside state.
There are five button handlers - `@X`, `@Y`, `@A`, `@B`, `@START`.
We need not define all the button handlers.

```c
@X{
  // Statements
}
```

# Issues
In case of any issues, post to the issues section of this GitHub repository.
Please provide a minimum reproducible example.

# Features on the queue
We are looking forward to implement the following features in the future.

- [ ] An optional `else` with `if`

[PyGame]: https://www.pygame.org/
