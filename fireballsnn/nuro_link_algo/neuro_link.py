from navec import Navec
from razdel import sentenize, tokenize
from slovnet import Morph

adj_propn_instrumental = {
    "вой": "вым",
    "ной": "ным",
    "кой": "ким",
    "ый": "ым",
    "ий": "им",
    "ая": "ой",
    "яя": "ей",
    "ое": "ым",
    "ее": "им",
    "-й": "-м",
    "-я": "-й",
    "-е": "-м"
}

adj_propn_genitive = {
    "вой": "вого",
    "ной": "ного",
    "кой": "кого",
    "ый": "ого",
    "ий": "ого",
    "ая": "ой",
    "яя": "ей",
    "ое": "ого",
    "ее": "его",
    "-й": "ого",
    "-я": "-й",# такие есть ввобще? еще окончание ие посмотерть
    "-е": "-их"
}

adj_propn_dative = {
    "вой": "вому",
    "ной": "ному",
    "кой": "кому",
    "ый": "ому",
    "ий": "ому",
    "ая": "ой",
    "яя": "ей",
    "ое": "ому",
    "ее": "ему",
    "-й": "ого",#хз
    "-я": "-й",#хз
    "-е": "-их"#хз
}

adj_propn_prepositional = {
    "вой": "вом",
    "ной": "ном",
    "кой": "ком",
    "ый": "ом",
    "ий": "ом",
    "ая": "ой",
    "яя": "ей",
    "ое": "ом",
    "ее": "ем",
    "-й": "ом",#хз
    "-я": "-й",#хз
    "-е": "-их"#хз
}
noun_instrumental = {
    "ья": "ьёй",
    "да": "дой",
    "она": "оном",
    "ок": "ком",
    "ие": "ием",
    "ись": "исью",
    "ия": "ией",
    "уд": "удом"
}

noun_genitive = {
    "ья": "ьи",
    "да": "ды",
    "она": "оны",
    "ок": "ка",
    "ие": "ия",
    "ись": "иси",
    "ия": "ии",
    "уд": "уда"
}

noun_dative = {
    "ья": "ье",
    "да": "де",
    "она": "оне",
    "ок": "ку",
    "ие": "ию",
    "ись": "иси",
    "ия": "ии",
    "уд": "уду"
}

noun_prepositional = {
    "ья": "ье",
    "да": "де",
    "она": "оне",
    "ок": "ке",
    "ие": "ии",
    "ись": "иси",
    "ия": "ии",
    "уд": "уде"
}
# все окончания обрабатываемых частей речи
# nominative_to_instrumental = {
#     "ADJ": adj_propn_im_vin,
#     "PROPN": adj_propn_im_vin ,
#     "NOUN": noun_im_vin,
# }
def case_detec(case):
    if case =='instrumental':
        return {
            "ADJ": adj_propn_instrumental,
            "PROPN": adj_propn_instrumental,
            "NOUN": noun_instrumental,
        }
    if case == 'genitive':
        return {
            "ADJ": adj_propn_genitive,
            "PROPN": adj_propn_genitive,
            "NOUN": noun_genitive,
        }
    if case == 'dative':
        return {
            "ADJ": adj_propn_dative,
            "PROPN": adj_propn_dative,
            "NOUN": noun_dative,
        }
    if case == 'prepositional':
        return {
            "ADJ": adj_propn_prepositional,
            "PROPN": adj_propn_prepositional,
            "NOUN": noun_prepositional,
        }


def solveStr(name, case):
    text = name
    if case == 'nominative' or case=='accusative':
        return name
    nominative_to_instrumental = case_detec(case)
    if len(list(nominative_to_instrumental))==0:
        return name
    # разбить на токены
    chunk = []
    for sent in sentenize(name):
        tokens = [_.text for _ in tokenize(sent.text)]
        chunk.append(tokens)

    # морфологический анализ
    markup = next(morph_ds.map([list(map(str.lower, chunk[0]))]))

    first_piece = []
    last_piece = markup.tokens.copy()

    # разделение на две смысловые части
    for token in last_piece.copy():
        first_piece.append(last_piece.pop(0))
        if token.pos == "NOUN":
            break

    # склонение из именительного падежа в творительный (прилагательных, существительных и сокращений)
    for i, token in enumerate(first_piece):
        if token.pos in [
            "ADJ",
            "NOUN",
            "PROPN",
        ]:
            suffixes = nominative_to_instrumental[token.pos].keys()
            # перебор по суффиксам (можно еще сделать по хеш-таблице, но тут маленький словать, поэтому можно не выпендриваться)
            for suffix in suffixes:
                # получаем длину для слайсинга (длина отрицательная для слайсинга)
                suffix_len = -len(suffix)

                # получаем суффикс, для сравнивания
                token_suffix = token.text[suffix_len:]
                if token_suffix == suffix:
                    # склоненный токен
                    result = (
                            token.text[:suffix_len]
                            + nominative_to_instrumental[token.pos][suffix]
                    )

                    # если капсом
                    if chunk[0][i].isupper():
                        text = text.replace(token.text.upper(), result.upper())
                    # если sentense case
                    elif chunk[0][i][:1].isupper():
                        if "-" in chunk[0][i]:
                            capitalzed_parts = [part.capitalize() for part in token.text.split("-")]
                            capitalzed_result = [part.capitalize() for part in result.split("-")]
                            text = text.replace(
                            "-".join(capitalzed_parts), "-".join(capitalzed_result)
                            )
                        else:
                            text = text.replace(
                                token.text.capitalize(), result.capitalize()
                            )
                    # если маленькими
                    elif chunk[0][i].islower():
                        text = text.replace(token.text.lower(), result.lower())
                    break

            # # если нулевое окончание (для слова "СУД", например)
            # if token.pos == "NOUN":
            #     result = token.text + "ом"
            #     text = text.replace(
            #         token.text.upper() if text.isupper() else token.text,
            #         result.upper() if text.isupper() else result,
            #     )
        # если сокращенное числительное
        elif token.pos == "NUM" and token.text.endswith("-й"):
            text = text.replace(
                "-Й" if chunk[0][i].isupper() else "-й",
                "-М" if chunk[0][i].isupper() else "-м",
            )
    return text


# данные для анализатора
navec_ds = Navec.load("nuro_link_algo/navec_news_v1_1B_250K_300d_100q.tar")
morph_ds = Morph.load("nuro_link_algo/slovnet_morph_news_v1.tar", batch_size=4)
morph_ds.navec(navec_ds)