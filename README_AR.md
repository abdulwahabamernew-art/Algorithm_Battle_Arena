# ساحة معارك الخوارزميات

[![CI](https://github.com/abdulwahabamernew-art/Algorithm_Battle_Arena/actions/workflows/ci.yml/badge.svg)](https://github.com/abdulwahabamernew-art/Algorithm_Battle_Arena/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22c55e.svg)](LICENSE)

**Algorithm Battle Arena** هو مختبر تفاعلي لعلوم الحاسوب يربط بين التحليل التقاربي النظري والتجارب المعيارية القابلة لإعادة الإنتاج. يوفر المشروع محاكاة بصرية، ومقارنات تجريبية، وخوارزميات مسارات شبكية، ومستشارًا لاختيار الخوارزمية باللغتين العربية والإنجليزية.

للقراءة بالإنجليزية: [README.md](README.md)

## نطاق المشروع

يضم المشروع ستة مختبرات تعليمية:

1. محاكاة خوارزميات الترتيب: Merge وQuick و3-way Quick وHeap وInsertion وSelection.
2. مقارنة معيارية مضبوطة مع تشغيل تمهيدي، وترتيب عشوائي للتجارب، وقياس الوسيط، وعدّ الكتابات والذاكرة المساعدة.
3. تجارب النمو التقاربي باستخدام نسب التضاعف.
4. مقارنة Linear وBinary وJump وInterpolation Search.
5. مقارنة BFS وDFS وDijkstra وA* على شبكات موزونة.
6. محلل للبيانات ومستشار خوارزمي وبنك أسئلة تفاعلي.

## التشغيل السريع

```bash
python -m venv .venv
source .venv/bin/activate              # Windows: .venv\\Scripts\\activate
python -m pip install -e .
python app.py
```

لتشغيل الاختبارات وواجهة سطر الأوامر:

```bash
python -m unittest discover -s tests -v
python -m arena --values "8,3,5,1,3,-2" --all-algorithms --trace --output outputs/demo
```

## هيكل المستودع

```text
app.py                  # نقطة تشغيل واجهة Gradio
arena/                  # الخوارزميات والقياسات والمقارنة وCLI
tests/                  # 19 اختبارًا في 6 وحدات اختبار
docs/                   # وثائق النطاق والمقاييس
examples/demo/          # أمثلة صغيرة قابلة للمراجعة
pyproject.toml          # بيانات الحزمة والاعتماديات
```

## المنهجية والقيود

تتأثر نتائج الزمن بجهاز التشغيل وإصدار Python ونمط البيانات وإعدادات التجربة. لذلك تُستخدم النتائج لفهم السلوك التجريبي ولا تُعد برهانًا عامًا على التعقيد النظري. يُنصح بتسجيل إصدار Python ونظام التشغيل ومواصفات الجهاز ونمط الإدخال والبذرة وعدد التكرارات ورقم Commit عند مقارنة النتائج.

توجد تعريفات القياسات التفصيلية في [docs/METRICS_AR.md](docs/METRICS_AR.md)، وحدود المشروع في [docs/SCOPE_AR.md](docs/SCOPE_AR.md).

## المساهمة والاستشهاد

يرجى قراءة [CONTRIBUTING.md](CONTRIBUTING.md) قبل فتح Pull Request. يمكن استخدام [CITATION.cff](CITATION.cff) للاستشهاد بالمشروع.

## الشكر والتقدير

إعداد عبدالوهاب يحيى محمد عامر، بإشراف نظري من د. معاذ الصبري، وإشراف عملي من م. محمد الوصابي.

## الترخيص

الكود منشور بموجب ترخيص MIT. راجع [LICENSE](LICENSE).
