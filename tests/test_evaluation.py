import csv
import time

from src.rag import answer_question


CSV_FILE = "tests/evaluation_questions.csv"


def run_evaluation():

    total = 0
    passed = 0
    failed = 0
    errors = 0

    print("\n======================================")
    print(" SupportPilot AI - Evaluation")
    print("======================================\n")

    with open(
        CSV_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            question = row["question"]

            expected = (
                row["expected"]
                .strip()
                .lower()
            )

            total += 1

          
            try:

                # ==========================================
                # CALL SUPPORTPILOT
                # ==========================================

                result = answer_question(
                    question
                )


                # ==========================================
                # READ ACTUAL INTENT
                # ==========================================

                intent = (
                    result.get(
                        "intent",
                        ""
                    )
                    .strip()
                    .lower()
                )

                handoff = result.get(
                    "handoff",
                    False
                )

             
                # ==========================================
                # DETERMINE ACTUAL RESULT
                # ==========================================

                if intent == "conversation":

                    actual = "conversation"

                elif intent == "unknown":

                    actual = "unknown"

                elif (
                    intent == "support"
                    and handoff is True
                ):

                    actual = "handoff"

                elif (
                    intent == "support"
                    and handoff is False
                ):

                    actual = "support_answer"

                else:

                    actual = "unknown"

                # ==========================================
                # Question and Expected
                # ==========================================
                
                print(f"Question: {question}")
                print(f"Expected: {expected}")              

                # ==========================================
                # DISPLAY RESULTS
                # ==========================================

                print(f"Actual:   {actual}")
                print(f"Intent:   {intent}")
                print(f"Handoff:  {handoff}")


                # ==========================================
                # COMPARE EXPECTED VS ACTUAL
                # ==========================================

                if actual == expected:

                    print(
                        "Result:   PASS ✅"
                    )

                    passed += 1

                else:

                    print(
                        "Result:   FAIL ❌"
                    )

                    failed += 1


            except Exception as e:

                print(
                    "Result:   ERROR ❌"
                )

                print(
                    f"Error:    {e}"
                )

                errors += 1
                failed += 1


            print(
                "--------------------------------------"
            )


            # ==========================================
            # RATE LIMIT PROTECTION
            # ==========================================

            print(
                "Waiting 6 seconds before next question..."
            )

            time.sleep(6)


    # ==============================================
    # FINAL SUMMARY
    # ==============================================

    print("\n======================================")
    print(" Evaluation Summary")
    print("======================================")

    print(
        f"Total Tests : {total}"
    )

    print(
        f"Passed      : {passed}"
    )

    print(
        f"Failed      : {failed}"
    )

    print(
        f"Errors      : {errors}"
    )


    if total > 0:

        accuracy = (
            passed / total
        ) * 100

        print(
            f"Accuracy    : {accuracy:.2f}%"
        )


    print("======================================\n")


if __name__ == "__main__":

    run_evaluation()