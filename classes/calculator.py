import math
from difflib import get_close_matches
from functools import reduce

from app.config import ALIASES, VALID, Operation


class Calculator:
    @staticmethod
    def basic_calculator(
        operation: Operation,
        numbers: list[float],
        decimals: int | None = None,
    ):
        """
        Gets numbers from user and do basic caltulations 
        on the basis of operation which is also provided by the user.
        Args:
            operation (Literal) : Operation which user asks to perform between the two numbers.
            numbers {list[float]} : The first number given by the user.
        Returns:
            str : A string which is the final answer of the user's query
        """
        if not numbers:
            raise ValueError("Numbers are mandatory to do calculations")

        print("\n--------------------------------------------------")
        print("🔧 TOOL CALLED: [CodeInterpreter.run_python_code]")
        print(f"📥 INPUT CODE:\n{operation}")
        print("--------------------------------------------------\n")

        match operation:
            case "addition":
                return sum(numbers)

            case "average":
                return sum(numbers) / len(numbers)

            case "maximum":
                return max(numbers)

            case "minimum":
                return min(numbers)

            case "subtraction":
                return reduce(lambda a, b: a - b, numbers)

            case "multiplication":
                return reduce(lambda a, b: a * b, numbers)

            case "division":
                if 0 in numbers[1:]:
                    raise ZeroDivisionError("Cannot divide by zero.")
                return reduce(lambda a, b: a / b, numbers)

            case "modulus":
                if 0 in numbers[1:]:
                    raise ZeroDivisionError("Cannot divide by zero.")
                return reduce(lambda a, b: a % b, numbers)

            case "power":
                return reduce(lambda a, b: a ** b, numbers)

            case "absolute":
                result = [abs(item) for item in numbers]
                return result[0] if len(result) == 1 else result

            case "round":
                result = [round(item, decimals) for item in numbers]
                return result[0] if len(result) == 1 else result

            case "floor":
                result = [math.floor(item) for item in numbers]
                return result[0] if len(result) == 1 else result

            case "ceil":
                result = [math.ceil(item) for item in numbers]
                return result[0] if len(result) == 1 else result

            case _:
                raise ValueError(f"Unexpected operation: {operation}")

    @staticmethod
    def scintific_calculator(operation: Operation, 
                             numbers: list[float], 
                             decimals: int | None = None):
        """
        Gets two numbers from user and do basic caltulations 
        on the basis of operation which is also provided by the user.
        Args:
            num1 {float} : The first number given by the user.
            num2 (float) : The second number given by the user.
            operation (str) : Operation whuch user asks to perform between the two numbers.
        Returns:
            str : A string which is the final answer of the user's query
        """
        


    @staticmethod
    def normalize_calculator(tool_input: dict):
        tool_input = tool_input.copy()

        if "operation" not in tool_input:
            raise ValueError("Calculator input must contain 'operation'")

        op = tool_input["operation"].lower().strip()

        if op in ALIASES:
            op = ALIASES[op]

        if op not in VALID:
            matches = get_close_matches(op, VALID, n=1, cutoff=0.75)

            if matches:
                op = matches[0]
            else:
                raise ValueError(f"Unsupported calculator operation: {op}")

        tool_input["operation"] = op
        return tool_input


if __name__ == "__main__":
    calculator = Calculator()
    print(calculator.basic_calculator("addition", [25, 56, 76, 434, 57]))
    # print(calculator.basic_calculator(25, 25, "subtract"))
    # print(calculator.basic_calculator(25, 25, "multiply"))
    # print(calculator.basic_calculator(25, 25, "divide"))
    # print(calculator.basic_calculator(25, 25, "power"))
    # print(calculator.basic_calculator(25, 25, "xyz"))
