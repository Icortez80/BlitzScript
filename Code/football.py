from textx import metamodel_from_file
import sys


# ---------------------------------------------------------------------------
# Control flow signals (used like exceptions to bubble up through the tree)
# ---------------------------------------------------------------------------

class FlagOnThePlay(Exception):
    """Themed runtime error."""
    def __init__(self, message):
        super().__init__(f"\n FLAG ON THE PLAY\n   {message}\n   15 yard penalty.\n")

class Turnover(Exception):
    """Signals a break out of a drive loop."""
    pass

class Punt(Exception):
    """Signals a skip to the next loop iteration."""
    pass

class GainSignal(Exception):
    """Carries a return value out of a play."""
    def __init__(self, value):
        self.value = value


# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------

class FootballInterpreter:
    def __init__(self):
        self.variables = {}
        self.plays = {}

    def get_value(self, value):
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            if value in self.variables:
                return self.variables[value]
            return value
        return value

    def run(self, program):
        for statement in program.statements:
            self.execute(statement)

    def execute(self, statement):
        cls_name = statement.__class__.__name__

        if cls_name == "CoinToss":
            print("Coin toss begins.")

        elif cls_name == "Announce":
            print(self.get_value(statement.value))

        elif cls_name == "SetVar":
            # Right-hand side may be a RunPlay that returns a value via gain
            if statement.value.__class__.__name__ == "RunPlay":
                result = self.call_play(statement.value.name)
                self.variables[statement.name] = result
            else:
                self.variables[statement.name] = self.get_value(statement.value)

        elif cls_name == "MathUpdate":
            if statement.name not in self.variables:
                raise FlagOnThePlay(
                    f"Illegal procedure: '{statement.name}' is not defined. "
                    f"Use 'set {statement.name} to 0' before updating it."
                )
            current = self.variables[statement.name]
            value = self.get_value(statement.value)

            if statement.op == "holding":
                self.variables[statement.name] = current + value
            elif statement.op == "false_start":
                self.variables[statement.name] = current - value
            elif statement.op == "double_team":
                self.variables[statement.name] = current * value
            elif statement.op == "split":
                if value == 0:
                    raise FlagOnThePlay(
                        f"Illegal procedure: cannot split '{statement.name}' by zero. "
                        f"That play is dead."
                    )
                self.variables[statement.name] = current // value

        elif cls_name == "DriveLoop":
            while self.check_condition(statement.condition):
                try:
                    for inner in statement.statements:
                        self.execute(inner)
                except Punt:
                    continue   # skip to next iteration
                except Turnover:
                    break      # exit loop entirely

        elif cls_name == "WhenBlock":
            if self.check_condition(statement.condition):
                for inner in statement.true_statements:
                    self.execute(inner)
            else:
                for inner in statement.false_statements:
                    self.execute(inner)

        elif cls_name == "PlayDef":
            self.plays[statement.name] = statement

        elif cls_name == "RunPlay":
            self.call_play(statement.name)

        elif cls_name == "Gain":
            value = self.get_value(statement.value)
            raise GainSignal(value)

        elif cls_name == "TurnoverStatement":
            raise Turnover()

        elif cls_name == "PuntStatement":
            raise Punt()

    def call_play(self, name):
        """Execute a named play and return its gain value (or None)."""
        play = self.plays.get(name)
        if play is None:
            raise FlagOnThePlay(
                f"Illegal procedure: play '{name}' is not in the playbook. "
                f"Define it with 'play {name} ... end' before calling it."
            )
        try:
            for inner in play.statements:
                self.execute(inner)
        except GainSignal as g:
            return g.value
        return None

    def check_condition(self, condition):
        cls_name = condition.__class__.__name__

        if cls_name == "DivisibleCondition":
            left = self.get_value(condition.left)
            first = self.get_value(condition.first)
            if first == 0:
                raise FlagOnThePlay(
                    "Illegal procedure: cannot use 'flagged_by 0'. "
                    "Division by zero on the field."
                )
            first_check = left % first == 0
            if condition.second is not None:
                second = self.get_value(condition.second)
                return first_check and left % second == 0
            return first_check

        elif cls_name == "CompareCondition":
            left = self.get_value(condition.left)
            right = self.get_value(condition.right)
            if condition.op == "<=":
                return left <= right
            elif condition.op == ">=":
                return left >= right
            elif condition.op == "==":
                return left == right
            elif condition.op == "<":
                return left < right
            elif condition.op == ">":
                return left > right

        return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python interpreter.py <program.fb>")
        sys.exit(1)

    mm = metamodel_from_file("football.tx")
    program = mm.model_from_file(sys.argv[1])

    interpreter = FootballInterpreter()
    try:
        interpreter.run(program)
    except FlagOnThePlay as e:
        print(e)


if __name__ == "__main__":
    main()