def generate_csv(entries):
    # Write the header row
    yield ','.join(['date', 'media_type', 'media_name', 'duration']) + '\n'
    # Write each row of data
    for entry in entries:
        yield ','.join([
            entry.date.strftime('%Y-%m-%d'),
            entry.media_type,
            entry.media_name,
            str(entry.duration)
        ]) + '\n'