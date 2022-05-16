any = []
for i in range(0,256):
    if i == 34:
        pass
    else:
        any.append(chr(i))
any = set(any)
any_regex = "≤" + '∥'.join(any) + "≥"
string_regex = '"' + "≤" + any_regex + "≤" + any_regex + "≥⋅" +"≥" +'"'

letter_regex = "≤a∥b∥c∥d∥e∥f∥g∥h∥i∥j∥k∥l∥m∥n∥o∥p∥q∥r∥s∥t∥u∥v∥w∥x∥y∥z∥A∥B∥C∥D∥E∥F∥G∥H∥I∥J∥K∥L∥M∥N∥O∥P∥Q∥R∥S∥T∥U∥V∥W∥X∥Y∥Z≥"
digit_regex = "≤0∥1∥2∥3∥4∥5∥6∥7∥8∥9≥"
id_regex = letter_regex + "≤" + letter_regex + "∥" + digit_regex + "≥⋅"
number = digit_regex + "≤" + digit_regex + "≥⋅"
simboles = "≤+∥-∥{∥}∥[∥]∥|∥≤..≥≥"
opp_ass_string = '"' + simboles + '"'
char_opp = "CHR"
any_set = "ANY"
set_regex = '"'+ "≤" + "≤" + letter_regex +"≤"+letter_regex+"≥⋅"+"≥" + "∥" + "≤"+ digit_regex+ "≤"+digit_regex+"≥⋅" + "≥" + "≥" +'"'
char_regex = "'" + "≤" + any_regex + "≤" + any_regex + "≥⋅" +"≥" +"'"
letter_or_numbers =letter_regex + "⋅∥" + digit_regex + "⋅"
