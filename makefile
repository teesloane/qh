bundle:
	pyinstaller main.py --onefile; mv dist/main dist/QH

clean:
	trash build; trash dist

# move executable to bin for testing.
shuffle:
	@echo "Removing old executable, copying over new..."; trash /usr/local/bin/QH; cp dist/main /usr/local/bin/QH;

dist: clean bundle shuffle