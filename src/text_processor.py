import re
import bioc
import tqdm
import spacy
import docopt
import medspacy
import pandas as pd
from bioc import BioCPipeline
from radtext.models import csv2bioc
from radtext.cmd.ner import load_yml
from radtext.core import BioCProcessor
from radtext.models.neg import NegCleanUp
from radtext.models.neg.neg import BioCNeg
from radtext.models.deid import BioCDeidPhi
from radtext.models.ner.radlex import RadLex4
from radtext.models.neg import NegRegexPatterns
from radtext.models.neg.match_ngrex import NegGrexPatterns

# from radtext.cmd.cmd_utils import process_options, process_file
from radtext.models.bioc_cdm_converter import convert_bioc_to_note_nlp
from radtext.models.ner.ner_regex import NerRegExExtractor, BioCNerRegex
from radtext.models.ner.ner_spacy import BioCNerSpacy, NerSpacyExtractor

from radtext.models.section_split.section_split_medspacy import (
    BioCSectionSplitterMedSpacy,
)
from radtext.models.bioc_cdm_converter import (
    convert_note_nlp_table_to_bioc,
    NOTE_TABLE_HEADERS,
)
from radtext.models.section_split.section_split_regex import (
    BioCSectionSplitterRegex,
    combine_patterns,
)


class TextProcessor:
    def __init__(self, resource_dir):
        self.resource_dir = resource_dir
        self.radlex = RadLex4(resource_dir / "Radlex4.1.xlsx")
        self.section_titles = self._load_section_titles()

    def _load_section_titles(self):
        with open(self.resource_dir / "section_titles.txt") as fp:
            section_titles = [line.strip() for line in fp]
        return section_titles

    # anonymizing
    def clean_text(self, text_file):
        with open(text_file, "r") as f:
            sentence = f.read()
        lower_sentence = sentence.lower()
        corrected_sentence = re.sub("and/or", "or", lower_sentence)
        corrected_sentence = re.sub(
            "(?<=[a-zA-Z])/(?=[a-zA-Z])", " or ", corrected_sentence
        )
        clean_sentence = corrected_sentence.replace("..", ".")
        punctuation_spacer = str.maketrans({key: f"{key} " for key in ".,"})
        clean_sentence = clean_sentence.translate(punctuation_spacer)
        clean_sentence = " ".join(clean_sentence.split())
        return clean_sentence

    def anonymize(self, text):
        passage = bioc.BioCPassage.of_text(text, 0)
        deid = BioCDeidPhi()
        deid_passage = deid.process_passage(passage)
        return deid_passage.text

    # conversions
    def csv2bioc(self, csv_file):
        df = pd.read_csv(csv_file, dtype=str)
        collection = csv2bioc.csv2bioc(df, "note_id", "note_text")
        assert len(collection.documents) == 2
        for i in range(1, 3):
            assert collection.documents[i - 1].text == df["note_text"][i]
        return collection.documents

    def bioc2cdm(self, xml_file):
        with open(xml_file) as fp:
            collection = bioc.load(fp)

        df = convert_bioc_to_note_nlp(collection)
        df = df[df["note_nlp_id"] == "S1"]
        assert df.iloc[0]["offset"] == 178
        return df

    def cdm2bioc(self, csv_file):
        df = pd.read_csv(csv_file, dtype=str)
        collection = convert_note_nlp_table_to_bioc(df)
        assert len(collection.documents) == 8

        for i in range(8):
            print(collection.documents[i])
            assert collection.documents[i].text == df["note_text"][i]
            assert collection.documents[i].id == df["note_id"][i]

            for k in NOTE_TABLE_HEADERS:
                if k not in ("note_id", "note_text"):
                    assert collection.documents[i].infons[k] == df[k][i]
        return collection.documents

    def cdm2bioc2(self, csv_file):
        df = pd.read_csv(csv_file, dtype=str)

        df1 = df.drop(["note_text"], axis=1)
        convert_note_nlp_table_to_bioc(df1)

        df1 = df.drop(["note_type_concept_id"], axis=1)
        collection = convert_note_nlp_table_to_bioc(df1)
        assert len(collection.documents) == 8
        return collection.document

    # NER
    def ner_regex(self, text):  # sourcery skip: class-extract-method
        phrases_file = self.resource_dir / "chexpert_phrases.yml"
        patterns = load_yml(phrases_file)
        extractor = NerRegExExtractor(patterns)
        processor = BioCNerRegex(extractor, name="chexpert_phrases")

        doc = bioc.BioCDocument()
        doc.add_passage(bioc.BioCPassage.of_text(text))
        processor.process_document(doc)

        return {ann.text for ann in doc.passages[0].annotations}

    def ner_radlex(self, text):
        nlp = spacy.load("en_core_web_sm", exclude=["ner", "parser", "senter"])
        matchers = self.radlex.get_spacy_matchers(nlp)
        extractor = NerSpacyExtractor(nlp, matchers)
        processor = BioCNerSpacy(extractor, "RadLex")

        doc = BioCPipeline()
        doc.add_passage(bioc.BioCPassage.of_text(text))
        processor.process_document(doc)

        return {ann.text for ann in doc.passages[0].annotations}

    # section splitting
    def document(self, text):
        # text = """findings: pa and lat cxr at 7:34 p.m.. heart and mediastinum are
        # stable. lungs are unchanged. air- filled cystic changes. no
        # pneumothorax. osseous structures unchanged scoliosis
        # impression: stable chest.
        # dictating
        # """
        return bioc.BioCDocument.of_text(text)

    def test_section_split_medspacy(self, document):
        nlp = medspacy.load(enable=["sectionizer"])
        splitter = BioCSectionSplitterMedSpacy(nlp)
        splitter.process_document(document)
        # assert len(document.passages) == 4
        # assert len(document.annotations) == 2
        # assert document.annotations[0].text == 'findings:'
        # assert document.annotations[1].text == 'impression:'
        return document

    def section_split_regex(self, document):
        pattern = combine_patterns(self.section_titles)
        splitter = BioCSectionSplitterRegex(pattern)
        splitter.process_document(document)
        # assert len(document.passages) == 4
        # assert len(document.annotations) == 2
        # assert document.annotations[0].text == 'findings:'
        return document

    # negation
    def process_file(self, src, dest, processor: BioCProcessor, level: int):
        with open(src) as fp:
            collection = bioc.load(fp)

        for doc in tqdm.tqdm(collection.documents):
            if level == bioc.DOCUMENT:
                processor.process_document(doc)
            elif level == bioc.PASSAGE:
                for passage in tqdm.tqdm(doc.passages, leave=False):
                    processor.process_passage(passage, doc.id)
            elif level == bioc.SENTENCE:
                for passage in tqdm.tqdm(doc.passages, leave=False):
                    for sentence in tqdm.tqdm(passage.sentences, leave=False):
                        processor.process_sentence(sentence, doc.id)

        with open(dest, "w") as fp:
            bioc.dump(collection, fp)

    def negation_detect(self, input_file, output_file):
        regex_actor = NegRegexPatterns()
        regex_actor.load_yml2("utils/patterns/regex_patterns.yml")
        ngrex_actor = NegGrexPatterns()
        ngrex_actor.load_yml2("utils/patterns/ngrex_patterns.yml")

        neg_actor = BioCNeg(regex_actor=regex_actor, ngrex_actor=ngrex_actor)
        cleanup_actor = NegCleanUp(False)
        pipeline = BioCPipeline()
        pipeline.processors = [neg_actor, cleanup_actor]
        self.process_file(input_file, output_file, pipeline, bioc.PASSAGE)


# processor = TextProcessor('utils')
# cleaned_text = processor.clean_text(text_file)
# anonymized_text = processor.anonymize(text)
# bioc_documents = processor.csv2bioc(csv_file)
