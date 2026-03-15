def fizzbuzz(n):
    if n % 15 == 0:
        return "FizzBuzz"
    elif n % 3 == 0:
        return "Fizz"
    elif n % 5 == 0:
        return "Buzz"
    else:
        return str(n)


def run_tui():
    print("=" * 30)
    print("      FizzBuzz TUI")
    print("=" * 30)
    print("Enter an integer to get its FizzBuzz result.")
    print("Type 'quit' or 'q' to exit.\n")

    while True:
        user_input = input("Enter a number: ").strip()

        if user_input.lower() in ("quit", "q"):
            print("Goodbye!")
            break

        try:
            n = int(user_input)
            print(f"  => {fizzbuzz(n)}\n")
        except ValueError:
            print("  [!] Invalid input. Please enter a whole number.\n")


if __name__ == "__main__":
    run_tui()
