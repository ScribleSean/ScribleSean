import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import render_memory  # noqa: E402
import update_readme  # noqa: E402

OLD_SVG = '<svg xmlns="http://www.w3.org/2000/svg">old</svg>'


def day(date, count=0, level='NONE', weekday=0):
    return {'date': date, 'contributionCount': count, 'contributionLevel': level, 'weekday': weekday}


def payload(calendar):
    return {'data': {'user': {'contributionsCollection': {'contributionCalendar': calendar}}}}


class RenderTests(unittest.TestCase):
    def test_no_weeks(self):
        svg = render_memory.render({'totalContributions': 0, 'weeks': []})
        ET.fromstring(svg)
        self.assertIn('0 active days', svg)

    def test_week_without_days(self):
        svg = render_memory.render({'totalContributions': 0, 'weeks': [{'contributionDays': []}]})
        ET.fromstring(svg)

    def test_all_zero_calendar(self):
        weeks = [{'contributionDays': [day('2026-01-0%d' % i, weekday=i) for i in range(1, 7)]}]
        svg = render_memory.render({'totalContributions': 0, 'weeks': weeks})
        ET.fromstring(svg)
        self.assertIn('0 active days and 0 contributions, 2026-01-01 to 2026-01-06', svg)

    def test_desc_and_text_are_escaped(self):
        weeks = [{'contributionDays': [day('<a&b>', 1, 'FIRST_QUARTILE'), day('"x"</desc>', 0)]}]
        svg = render_memory.render({'totalContributions': '<script>&', 'weeks': weeks})
        root = ET.fromstring(svg)
        ns = {'s': 'http://www.w3.org/2000/svg'}
        self.assertIn('<a&b> to "x"</desc>', root.find('s:desc', ns).text)
        self.assertIn('<script>&', root.find('s:text', ns).text)
        self.assertNotIn('<script>', svg)


class UpdateTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        (self.root / 'assets').mkdir()
        self.card = self.root / 'assets' / 'memory-card.svg'
        self.card.write_text(OLD_SVG)
        patcher = mock.patch.object(update_readme, 'ROOT', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_with(self, data):
        source = self.root / 'payload.json'
        source.write_text(json.dumps(data))
        with mock.patch.object(sys, 'argv', ['update_readme.py', str(source)]):
            update_readme.main()

    def test_api_error_keeps_old_file(self):
        with self.assertRaises(RuntimeError):
            self.run_with({'errors': [{'message': 'boom'}]})
        self.assertEqual(self.card.read_text(), OLD_SVG)

    def test_api_error_from_network_keeps_old_file(self):
        body = io.BytesIO(json.dumps({'errors': [{'message': 'boom'}]}).encode())
        env = {'PROFILE_LOGIN': 'someone', 'GH_TOKEN': 'not-a-real-token'}
        with mock.patch.dict('os.environ', env), \
             mock.patch.object(sys, 'argv', ['update_readme.py']), \
             mock.patch('urllib.request.urlopen', return_value=body):
            with self.assertRaises(RuntimeError):
                update_readme.main()
        self.assertEqual(self.card.read_text(), OLD_SVG)

    def test_missing_user_keeps_old_file(self):
        with self.assertRaises(RuntimeError):
            self.run_with({'data': {'user': None}})
        self.assertEqual(self.card.read_text(), OLD_SVG)

    def test_empty_calendar_writes_valid_svg(self):
        self.run_with(payload({'totalContributions': 0, 'weeks': []}))
        ET.fromstring(self.card.read_text())

    def test_bad_svg_keeps_old_file(self):
        with mock.patch.object(render_memory, 'render', return_value='<svg><rect></svg>'):
            with self.assertRaises(ET.ParseError):
                self.run_with(payload({'totalContributions': 0, 'weeks': []}))
        self.assertEqual(self.card.read_text(), OLD_SVG)

    def test_good_calendar_replaces_file(self):
        weeks = [{'contributionDays': [day('2026-01-01', 3, 'SECOND_QUARTILE')]}]
        self.run_with(payload({'totalContributions': 3, 'weeks': weeks}))
        self.assertIn('1 active days and 3 contributions', self.card.read_text())


if __name__ == '__main__':
    unittest.main()
