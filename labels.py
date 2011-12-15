# from ASTNodes import SENTENCE, NUMBER, LETTER
# import ASTNodes
# print ASTNodes.FUNCTION
deallocationLabel =  "deallocate_label"
overFlowLabel = "overflow_label"
divisionByZeroLabel = "division_by_zero_label"
osReturnLabel = "os_return"
printNumberLabel = "print_number"
printLetterLabel = "print_letter"
printSentenceLabel = "print_sentence"
inputNumberLabel = "inputintfmt"
inputLetterLabel = "inputcharfmt"

overFlowMessageDict = {overFlowLabel:("int_overflow", "Error integer overflow" ),
                       divisionByZeroLabel:("div_zero", "Error division by zero")}
                       
spokeTypeDict = {"sentence":(printSentenceLabel, "outputstringfmt", "%s"),
                 "number":(printNumberLabel,"outputintfmt", "%ld"),
                 "letter":(printLetterLabel,"outputcharfmt", "%c")}