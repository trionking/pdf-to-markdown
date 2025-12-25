#!/usr/bin/env python3
"""
PDF to Markdown Converter with Translation - GUI 버전
- PDF 선택 시 → Markdown 변환
- MD 선택 시 → 번역
- 배치 번역으로 속도 향상 (번호 마커 사용)

설치:
    pip install pymupdf4llm deep-translator
"""

import re
import threading
from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


LANGUAGES = {
    "번역 안함": None,
    "한국어": "ko",
    "영어": "en",
    "일본어": "ja",
    "중국어 (간체)": "zh-CN",
    "중국어 (번체)": "zh-TW",
}

SOURCE_LANGUAGES = {
    "자동 감지": "auto",
    "중국어 (간체)": "zh-CN",
    "중국어 (번체)": "zh-TW",
    "영어": "en",
    "일본어": "ja",
    "한국어": "ko",
}


class PDFToMarkdownGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF to Markdown Converter")
        self.root.geometry("700x550")
        self.root.resizable(True, True)

        self.input_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.extract_images = tk.BooleanVar(value=False)
        self.page_chunks = tk.BooleanVar(value=False)
        self.source_lang = tk.StringVar(value="자동 감지")
        self.target_lang = tk.StringVar(value="번역 안함")
        self.is_processing = False
        self.translator_available = False

        self.create_widgets()
        self.check_dependencies()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 입력 파일
        input_frame = ttk.LabelFrame(main_frame, text="입력 파일 (PDF → MD 변환, MD → 번역)", padding="5")
        input_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Entry(input_frame, textvariable=self.input_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(input_frame, text="파일 선택", command=self.browse_file).pack(side=tk.LEFT)

        # 출력 폴더
        output_frame = ttk.LabelFrame(main_frame, text="출력 폴더 (비워두면 입력 파일과 같은 폴더)", padding="5")
        output_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Entry(output_frame, textvariable=self.output_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        ttk.Button(output_frame, text="폴더 선택", command=self.browse_output).pack(side=tk.LEFT)

        # PDF 옵션
        option_frame = ttk.LabelFrame(main_frame, text="PDF 변환 옵션", padding="5")
        option_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Checkbutton(option_frame, text="이미지 추출", variable=self.extract_images).pack(anchor=tk.W)
        ttk.Checkbutton(option_frame, text="페이지별 구분선", variable=self.page_chunks).pack(anchor=tk.W)
        ttk.Label(option_frame, text="* 표가 깨진 경우 AI(Claude 등)로 검토/수정 권장",
                  foreground="gray").pack(anchor=tk.W)

        # 번역 옵션
        translate_frame = ttk.LabelFrame(main_frame, text="번역 옵션 (Google Translate - 배치 번역)", padding="5")
        translate_frame.pack(fill=tk.X, pady=(0, 10))
        lang_row = ttk.Frame(translate_frame)
        lang_row.pack(fill=tk.X, pady=2)
        ttk.Label(lang_row, text="소스:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(lang_row, textvariable=self.source_lang, values=list(SOURCE_LANGUAGES.keys()), state="readonly", width=12).pack(side=tk.LEFT, padx=(0, 15))
        ttk.Label(lang_row, text="번역:").pack(side=tk.LEFT, padx=(0, 5))
        ttk.Combobox(lang_row, textvariable=self.target_lang, values=list(LANGUAGES.keys()), state="readonly", width=12).pack(side=tk.LEFT)

        # 버튼
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        self.run_btn = ttk.Button(btn_frame, text="실행", command=self.start_processing, width=12)
        self.run_btn.pack(side=tk.LEFT, padx=(0, 10))
        self.progress_var = tk.DoubleVar(value=0)
        self.progress = ttk.Progressbar(btn_frame, mode='determinate', variable=self.progress_var, maximum=100)
        self.progress.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.progress_label = ttk.Label(btn_frame, text="0%", width=5)
        self.progress_label.pack(side=tk.LEFT)

        # 로그
        log_frame = ttk.LabelFrame(main_frame, text="로그", padding="5")
        log_frame.pack(fill=tk.BOTH, expand=True)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, state=tk.DISABLED)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 상태바
        self.status_var = tk.StringVar(value="준비됨")
        ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN).pack(fill=tk.X, pady=(10, 0))

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{datetime.now().strftime('%H:%M:%S')}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def check_dependencies(self):
        try:
            import pymupdf4llm
            self.log("pymupdf4llm OK")
        except ImportError:
            self.log("경고: pip install pymupdf4llm 필요")
        try:
            from deep_translator import GoogleTranslator
            self.translator_available = True
            self.log("deep-translator OK")
        except ImportError:
            self.log("경고: pip install deep-translator 필요")

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="파일 선택",
            filetypes=[("PDF/Markdown", "*.pdf *.md"), ("PDF", "*.pdf"), ("Markdown", "*.md"), ("모든 파일", "*.*")]
        )
        if filename:
            self.input_path.set(filename)
            ext = Path(filename).suffix.lower()
            if ext == '.pdf':
                self.log(f"PDF: {Path(filename).name} → MD 변환")
            elif ext == '.md':
                self.log(f"MD: {Path(filename).name} → 번역")

    def browse_output(self):
        folder = filedialog.askdirectory(title="출력 폴더 선택")
        if folder:
            self.output_path.set(folder)
            self.log(f"출력 폴더: {folder}")

    def start_processing(self):
        if self.is_processing:
            return
        input_path = self.input_path.get().strip()
        if not input_path:
            messagebox.showwarning("입력 필요", "파일을 선택하세요.")
            return
        if not Path(input_path).exists():
            messagebox.showerror("파일 없음", f"파일을 찾을 수 없습니다:\n{input_path}")
            return

        self.is_processing = True
        self.run_btn.config(state=tk.DISABLED)
        self.set_progress(0)
        self.status_var.set("처리 중...")
        threading.Thread(target=self.run_processing, daemon=True).start()

    def set_progress(self, percent):
        self.progress_var.set(percent)
        self.progress_label.config(text=f"{int(percent)}%")

    def run_processing(self):
        try:
            input_path = Path(self.input_path.get())
            output_folder = self.output_path.get().strip() or None
            ext = input_path.suffix.lower()

            if ext == '.pdf':
                self.convert_pdf(input_path, output_folder)
            elif ext == '.md':
                if self.target_lang.get() == "번역 안함":
                    self.root.after(0, lambda: messagebox.showinfo("알림", "MD 파일은 번역 언어를 선택하세요."))
                else:
                    self.translate_file(input_path, output_folder)
            else:
                self.root.after(0, lambda: messagebox.showwarning("지원 안함", f"지원하지 않는 형식: {ext}"))
                return

            self.root.after(0, lambda: self.status_var.set("완료!"))
            self.root.after(0, lambda: messagebox.showinfo("완료", "작업이 완료되었습니다!"))
        except Exception as e:
            self.root.after(0, lambda: self.log(f"오류: {e}"))
            self.root.after(0, lambda: messagebox.showerror("오류", str(e)))
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.run_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.set_progress(100 if self.status_var.get() == "완료!" else 0))

    def translate_text(self, text, source_lang, target_lang, progress_offset=0, progress_range=100):
        """배치 번역으로 속도 향상 (번호 마커 사용)"""
        from deep_translator import GoogleTranslator
        import time
        if not text.strip():
            return text

        lines = text.split('\n')
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        total = len(lines)
        result = [''] * total

        # 번역할 줄과 스킵할 줄 분류
        to_translate = []
        for i, line in enumerate(lines):
            if not line.strip() or line.strip().startswith('![') or line.strip().startswith('```') or re.match(r'^[\|\-\:\s]+$', line.strip()):
                result[i] = line
            else:
                to_translate.append((i, line))

        # 배치 크기 설정
        BATCH_SIZE = 15  # 한 번에 번역할 줄 수 (마커 포함하여 줄임)
        MAX_CHARS = 3500  # 배치당 최대 문자 수

        batches = []
        current_batch = []
        current_chars = 0

        for idx, line in to_translate:
            line_len = len(line) + 10  # 마커 길이 포함
            if current_batch and (len(current_batch) >= BATCH_SIZE or current_chars + line_len > MAX_CHARS):
                batches.append(current_batch)
                current_batch = []
                current_chars = 0
            current_batch.append((idx, line))
            current_chars += line_len

        if current_batch:
            batches.append(current_batch)

        self.root.after(0, lambda: self.log(f"번역 배치: {len(batches)}개 ({len(to_translate)}줄)"))

        # 배치 단위로 번역
        for batch_num, batch in enumerate(batches):
            percent = progress_offset + ((batch_num + 1) / len(batches)) * progress_range
            self.root.after(0, lambda p=percent: self.set_progress(p))

            if batch_num > 0 and batch_num % 10 == 0:
                self.root.after(0, lambda n=batch_num, t=len(batches): self.log(f"번역 진행: {n}/{t} 배치"))

            # 번호 마커로 줄 구분
            marked_lines = []
            for j, (_, line) in enumerate(batch):
                marked_lines.append(f"<#{j}#>{line}")
            combined_text = "\n".join(marked_lines)

            try:
                translated = translator.translate(combined_text[:4500])
                if translated:
                    # 마커로 분리
                    translated_lines = []
                    pattern = r'<#(\d+)#>'
                    parts = re.split(pattern, translated)
                    for k in range(1, len(parts), 2):
                        if k + 1 < len(parts):
                            translated_lines.append(parts[k + 1].strip())

                    for j, (idx, original) in enumerate(batch):
                        if j < len(translated_lines) and translated_lines[j]:
                            result[idx] = translated_lines[j]
                        else:
                            result[idx] = original
                else:
                    for idx, line in batch:
                        result[idx] = line

                time.sleep(0.1)

            except Exception as e:
                self.root.after(0, lambda err=str(e)[:50]: self.log(f"배치 오류, 개별 번역: {err}"))
                for idx, line in batch:
                    try:
                        translated = translator.translate(line[:4500])
                        result[idx] = translated if translated else line
                        time.sleep(0.03)
                    except:
                        result[idx] = line

        self.root.after(0, lambda: self.log(f"번역 완료: {total}줄"))
        return '\n'.join(result)

    def translate_file(self, input_path, output_folder=None):
        self.root.after(0, lambda: self.log(f"번역: {input_path.name}"))
        self.root.after(0, lambda: self.set_progress(5))
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        output_folder = Path(output_folder) if output_folder else input_path.parent
        output_folder.mkdir(parents=True, exist_ok=True)
        output_path = output_folder / f"{input_path.stem}.md"

        source = SOURCE_LANGUAGES.get(self.source_lang.get(), "auto")
        target = LANGUAGES.get(self.target_lang.get(), "ko")
        self.root.after(0, lambda: self.log(f"번역 중: {source} → {target}"))

        translated = self.translate_text(content, source, target, progress_offset=5, progress_range=90)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated)
        self.root.after(0, lambda: self.set_progress(100))
        self.root.after(0, lambda: self.log(f"저장: {output_path}"))

    def sanitize_filename(self, name):
        """파일명에서 특수문자, 한글, 공백 제거"""
        sanitized = re.sub(r'[^a-zA-Z0-9]', '', name)
        return sanitized[:20] if sanitized else "pdf"

    def simplify_image_names(self, image_folder, md_text, rel_folder):
        """이미지 파일명 간소화"""
        import shutil
        image_files = sorted(image_folder.glob("*.*"))

        for i, img_path in enumerate(image_files, 1):
            ext = img_path.suffix.lower()
            new_name = f"img_{i:03d}{ext}"
            new_path = image_folder / new_name
            old_ref = img_path.name

            if img_path != new_path:
                shutil.move(str(img_path), str(new_path))

            md_text = md_text.replace(old_ref, new_name)

        md_text = md_text.replace(str(image_folder).replace("\\", "/"), rel_folder)
        md_text = md_text.replace(str(image_folder), rel_folder)

        self.root.after(0, lambda n=len(image_files): self.log(f"이미지 {n}개 간소화 완료"))
        return md_text

    def convert_pdf(self, pdf_path, output_folder=None):
        import pymupdf4llm
        self.root.after(0, lambda: self.log(f"변환: {pdf_path.name}"))
        self.root.after(0, lambda: self.set_progress(10))

        output_folder = Path(output_folder) if output_folder else pdf_path.parent
        output_folder.mkdir(parents=True, exist_ok=True)
        output_path = output_folder / f"{pdf_path.stem}.md"

        image_folder = None
        simple_image_folder = None
        if self.extract_images.get():
            simple_name = self.sanitize_filename(pdf_path.stem)
            simple_image_folder = output_folder / f"{simple_name}_images"
            simple_image_folder.mkdir(parents=True, exist_ok=True)
            image_folder = simple_image_folder

        rel_image_folder = f"./{simple_image_folder.name}" if simple_image_folder else None

        if self.page_chunks.get():
            chunks = pymupdf4llm.to_markdown(str(pdf_path), page_chunks=True, write_images=self.extract_images.get(), image_path=str(image_folder) if image_folder else None)
            md_text = ""
            for i, chunk in enumerate(chunks):
                md_text += chunk.get('text', '') if isinstance(chunk, dict) else str(chunk)
                md_text += f"\n\n---\n<!-- Page {i+1} -->\n\n"
        else:
            md_text = pymupdf4llm.to_markdown(str(pdf_path), write_images=self.extract_images.get(), image_path=str(image_folder) if image_folder else None)

        if image_folder and image_folder.exists():
            md_text = self.simplify_image_names(image_folder, md_text, rel_image_folder)

        self.root.after(0, lambda: self.set_progress(40))
        self.root.after(0, lambda: self.log("PDF 변환 완료"))

        if self.target_lang.get() != "번역 안함" and self.translator_available:
            source = SOURCE_LANGUAGES.get(self.source_lang.get(), "auto")
            target = LANGUAGES.get(self.target_lang.get(), "ko")
            self.root.after(0, lambda: self.log(f"번역 중: {source} → {target}"))
            md_text = self.translate_text(md_text, source, target, progress_offset=40, progress_range=55)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_text)
        self.root.after(0, lambda: self.set_progress(100))
        self.root.after(0, lambda: self.log(f"저장: {output_path}"))


def main():
    root = tk.Tk()
    PDFToMarkdownGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
