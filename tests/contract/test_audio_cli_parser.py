"""
Contract tests for audio_processor CLI parser.
Tests FR-015, FR-016, FR-017, FR-018: CLI arguments and options.
"""



class TestAudioCliParserContract:
    """Test that CLI parser accepts required arguments."""

    def test_create_cli_parser_exists(self):
        """Test that CLI parser creation function exists."""
        from audio_processor.cli import create_parser
        assert callable(create_parser)

    def test_parser_accepts_audio_files_positional(self):
        """Test that parser accepts audio files as positional arguments."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio1.mp3', 'audio2.wav'])
        assert hasattr(args, 'audio_files')
        assert len(args.audio_files) == 2

    def test_parser_accepts_format_option(self):
        """Test that parser accepts --format option."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio.mp3', '--format', 'json'])
        assert hasattr(args, 'format')
        assert args.format == 'json'

    def test_parser_accepts_model_option(self):
        """Test that parser accepts --model option."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio.mp3', '--model', 'large-v3'])
        assert hasattr(args, 'model')
        assert args.model == 'large-v3'

    def test_parser_accepts_quantization_option(self):
        """Test that parser accepts --quantization option."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio.mp3', '--quantization', '8bit'])
        assert hasattr(args, 'quantization')
        assert args.quantization == '8bit'

    def test_parser_accepts_language_option(self):
        """Test that parser accepts --language option."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio.mp3', '--language', 'es'])
        assert hasattr(args, 'language')
        assert args.language == 'es'

    def test_parser_accepts_batch_size_option(self):
        """Test that parser accepts --batch-size option."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio.mp3', '--batch-size', '24'])
        assert hasattr(args, 'batch_size')
        assert args.batch_size == 24

    def test_parser_accepts_output_option(self):
        """Test that parser accepts --output option."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio.mp3', '--output', 'results.json'])
        assert hasattr(args, 'output')
        assert args.output == 'results.json'

    def test_parser_accepts_verbose_flag(self):
        """Test that parser accepts --verbose flag."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio.mp3', '--verbose'])
        assert hasattr(args, 'verbose')
        assert args.verbose is True

    def test_parser_accepts_quiet_flag(self):
        """Test that parser accepts --quiet flag."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio.mp3', '--quiet'])
        assert hasattr(args, 'quiet')
        assert args.quiet is True

    def test_parser_default_values(self):
        """Test that parser has correct default values."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args(['audio.mp3'])
        assert args.format == 'plain'
        assert args.model == 'medium'
        assert args.quantization == 'none'  # Changed from '4bit' due to MLX compatibility
        assert args.verbose is False
        assert args.quiet is False

    def test_parser_accepts_all_options_combined(self):
        """Test that parser accepts all options together."""
        from audio_processor.cli import create_parser
        parser = create_parser()
        args = parser.parse_args([
            'audio1.mp3', 'audio2.wav',
            '--format', 'json',
            '--model', 'base',
            '--quantization', '4bit',
            '--language', 'en',
            '--batch-size', '16',
            '--output', 'output.json',
            '--verbose'
        ])
        assert len(args.audio_files) == 2
        assert args.format == 'json'
        assert args.model == 'base'
        assert args.quantization == '4bit'
        assert args.language == 'en'
        assert args.batch_size == 16
        assert args.output == 'output.json'
        assert args.verbose is True
