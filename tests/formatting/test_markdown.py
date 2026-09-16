from tcc_kit.formatting.markdown import parse_manuscript


def test_parser_preserves_supported_block_order(tmp_path):
    text = "# Título\n\nTexto de exemplo.\n\n- Item\n"
    blocks = parse_manuscript(text, tmp_path)
    assert [block.kind for block in blocks] == ["heading", "paragraph", "list"]
    assert blocks[0].text == "Título"
    assert blocks[2].items == ["Item"]


def test_parser_flags_remote_images_and_html(tmp_path):
    blocks = parse_manuscript("![x](https://exemplo.test/x.png)\n\n<div>html</div>", tmp_path)
    assert [block.kind for block in blocks] == ["diagnostic", "diagnostic"]


def test_frontmatter_is_one_metadata_block_not_body_text(tmp_path):
    blocks = parse_manuscript('---\ntitle: "Meu título"\nauthor: "Ana"\n---\n\n# Introdução', tmp_path)
    assert blocks[0].kind == "frontmatter"
    assert [block.kind for block in blocks[1:]] == ["heading"]
