Support for loading and saving NedGraphics pattern (.pat) files.
================================================================

Usage examples:

```
import pat

# Load a pattern file
f = open('example.pat', 'rb')
pattern = loads(f.read())
f.close()
    
# Save pattern file as an image
pattern.to_image().save('example.png')
    
# Save pattern file as an image converted to a full repeat
pattern.to_image(True).save('example_full_repeat.png')
    
# Create a pattern from an image
pattern = Pattern.from_image(Image.open('example.png'), 162)
    
# Save a pattern file
f = open('example.pat', 'wb')
f.write(dumps(pattern))
f.close()
```

**Requirements: Python 2.6, PIL** (Tested using Python 2.6 (as that's the version the project I wrote it for is using), should work with later versions though Python 3+ would require some minor changes.)


