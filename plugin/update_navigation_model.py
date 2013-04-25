import bsddb.db as db 

conn = db.DB()
filename = vim.eval("g:clic_filename")
conn.open(filename, None, db.DB_BTREE, db.DB_RDONLY)

def GetAllEntriesInternal(s):
    cursor = conn.cursor()
    entry = cursor.set_range(s)

    while not entry is None and entry[0].startswith(s):
        first = entry[0][len(s):]
        for sep in ['F', 'FI', 'FT', 'EA', 'E']:
            first = first.replace('@%s@' % sep, ' :: ')
        first = first.replace('@', ' ')
        parts = first.split(' :: ')
        for i in range(len(parts)):
            if '>#' in parts[i]:
                parts[i] = parts[i][:parts[i].index('>#')] + '<>'
            if '#' in parts[i]:
                parts[i] = parts[i][:parts[i].index('#')] + '()'
        first = ' :: '.join(parts)
        second = entry[1]
        yield (first, second)
        entry = cursor.next()

    cursor.close()

def GetAllOccurences(q, classes_only):
    for r in q[1].split('\t'):
        details = r.split(':')
        if len(details) <= 1:
            continue

        if int(details[-1]) >= 40:
            continue

        if classes_only and int(details[-1]) not in [1, 2, 3, 4, 5, 20, 31, 32]:
            continue

        if int(details[-1] in [10, 27, 28, 29]):
            continue

        yield (q[0], r)

def GetAllEntries(classes_only):
    ret = []
    for ltr in range(ord('A'), ord('Z') + 1):
        for q in GetAllEntriesInternal('c:@%s@' % chr(ltr)):
            for z in GetAllOccurences(q, classes_only):
                ret.append((z[0], z[1]))
    return ret

last_files_list = []
def GetAllEntryNames(classes_only):
    global last_files_list
    entries = GetAllEntries(classes_only)
    last_files_list = [x[1] for x in entries]
    return [x[0] + (' [%d]' % (i + 1) + (' (%s)' % x[1].split(':')[-1])) for i, x in enumerate(entries)]

def jumpToLocation(filename, line, column):
  if filename != vim.current.buffer.name:
    try:
      vim.command("edit %s" % filename)
    except:
      # For some unknown reason, whenever an exception occurs in
      # vim.command, vim goes crazy and output tons of useless python
      # errors, catch those.
      return
  else:
    vim.command("normal m'")
  vim.current.window.cursor = (line, column - 1)

def NavigateToEntry(entry):
    global last_files_list
    if '[' in entry:
        id = int(entry[entry.find('[') + 1:entry.find(']')]) - 1
        file_entry = last_files_list[id]
        arr = file_entry.split(':')
        if len(arr) >= 3:
            jumpToLocation(arr[0], int(arr[1]), int(arr[2]))

def ExtractSymbol(entry):
    return entry[:entry.find('[') - 1]

