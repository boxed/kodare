# Copyright Anders Hovmoller. This code is free for all use according to the CC0 license model of Creative Commons.

# TODO: handle "[NSDate descriptionWithCalendarFormat:"%H:%M:%S" timeZone:None locale: None]" nicer
# TODO: a block that is only populated by comments or totally empty needs to have a 'pass' added
import re

def massage_class_start(line):
	return re.sub(r'@implementation\s*(?P<class_name>\w*)\s*', r'class \g<class_name> {', line)

def massage_preprocessor_stuff(source):
	return re.sub(r'\s*(?P<foo>#.*)\n', '\g<foo>;\n', source)

def split_blocks(source):
	source = massage_preprocessor_stuff(source)
	source = massage_class_start(source)
	indent = 0
	result = []
	for r in source.split('{'):
		r2 = r.split('}')
		result.append((r2[0], indent))
		for r3 in r2[1:]:
			indent -= 1
			result.append((r3, indent))
		indent += 1
	return result

def objc_to_python(source):
	result = ''
	last_indent = 0
	last_raw_line = ''
	for block, indent in split_blocks(source):
		if last_indent < indent:
			result += ':'
		for line in objc_block_to_python(block):
			if line.startswith('def ') or line.startswith('@') or line.startswith('class '):
				if not last_raw_line.startswith('@'): # annotations should not generate a newline
					result += '\n'
			result += ('\n%s%s' % (''.join(['\t' for x in range(0, indent)]), line)).rstrip()
			last_raw_line = line
		last_indent = indent
	return result#re.sub(r'([^:])\n\n', r'\1\n', result)

def fix_if_and_while(line):
	m = re.match(r'if\s*\((?P<expression>.*)\)', line)
	if m:
		return 'if %(expression)s' % m.groupdict()

	m = re.match(r'while\s*\((?P<expression>.*)\)', line)
	if m:
		return 'while %(expression)s' % m.groupdict()

	m = re.match(r'for\s*\((?P<a>.*)\s?in\s?(?P<b>.*)\)', line)
	if m:
		line = 'for %(a)s in %(b)s' % m.groupdict()
		m = re.match('(?P<a>for )\w*\s*\*(?P<b>.*)', line) # match a declared type
		if m:
			line = '%(a)s %(b)s' % m.groupdict()
	return line

def split_list(list, chunk_size):
    return [list[offset:offset+chunk_size] for offset in range(0, len(list), chunk_size)]

def convert_to_python_call(method_call, add_self=False):
	if re.match(r".*'[^']*(?P<foo>\:).*'", method_call): # if a function has a string as argument with a : in it we ignore it instead of trying to handle this case
		return method_call
	m = re.match(r'(?P<object>[^\s]*)\s*(?P<rest>.*)', method_call)
	method_parts = [x for x in re.split(r'[:\s]', m.groupdict()['rest']) if x != '']
	if len(method_parts) == 1:
		return '%s.%s(%s) ' % (m.groupdict()['object'], method_parts[0], 'self' if add_self else '')
	
	keys = []
	values = []
	if add_self:
		values.append('self')
	for key, value in split_list(method_parts, 2):
		keys.append(key)
		values.append(value)
	
	return '%s.%s_(%s)' % (m.groupdict()['object'], '_'.join(keys), ', '.join(values))
	
def fix_variable_declaration_assignment(line):
	# Fraction *frac = [[Fraction alloc] init];
	m = re.match(r'(?P<type>\w*)(?P<foo>\s*\**\s*)(?P<variable>[^=]*)=(?P<rest>.*)',  line)
	if m and m.groupdict()['variable'] != '':
		# remove "Type*" at the start of the line since python has no type declarations
		return '%(variable)s = %(rest)s' % m.groupdict()
	return line
	
def fix_method_declaration(line):
	if line.startswith('-') or line.startswith('+'):
		static = False
		if line.startswith('+'):
			static = True
		line = line[1:].replace('\n', ' ')
		line = re.sub(r'\(.*?\)', '', line).strip()
		replacement_key = '__object_replacement_for_fix_method_declaration__'
		return '%sdef %s' % ('@staticmethod\n' if static else '', convert_to_python_call('%s %s' % (replacement_key, line), add_self=not static).replace('%s.'% replacement_key, ''))
	return line
	
def fix_method_call(line):
	# method call, these can be nested, that's why I loop here
	while True:
		m = re.match(r'(?P<pre>.*)\[(?P<method_call>.*?)\](?P<post>.*)', line)
		if m:
			line = '%s%s%s' % (m.groupdict()['pre'], convert_to_python_call(m.groupdict()['method_call']), m.groupdict()['post'])
		else:
			return line
			
def fix_spaces(line):
	return line.replace('\t', ' ').replace('  ', ' ').replace('  ', ' ').replace('  ', ' ') # a little ugly hack
	
def objc_block_to_python(source):
	source = source.replace('@"', '"').replace('"', "'")
	source = source.replace(']', '] ') # this is a little hack so we support [[foo bar]asd] and not only [[foo bar] asd] (notice the space!)

	lines = []
	for line in [x.strip() for x in source.split(';')]:
		# comment lines that begin with // end with newline
		if line.startswith('//'):
			lines.extend([x.strip() for x in line.split('\n')])
		else:
			lines.append(line)
			
	filters = [
		lambda line: line.replace('\n', ' '),
		lambda line: line.replace('%@', '%s'),
		lambda line: line.replace('&&', ' and ').replace('||', ' or '),
		lambda line: line.replace('@end', ''),
		fix_variable_declaration_assignment,
		fix_method_declaration,
		fix_method_call,
		fix_if_and_while,
		fix_spaces,
		lambda line: line.replace(') )', '))'),
		lambda line: re.sub(r'(?P<pre>.*)@selector\((?P<expression>[^)]*)\)(?P<post>.*)', '\g<pre>\g<expression>\g<post>', line),
		lambda line: re.sub(r'(?P<pre>.*)!(?P<variable>\w*)', '\g<pre>not \g<variable>', line),
		lambda line: re.sub(r'(?P<pre>.*)\b(?P<nil>nil)\b(?P<post>.*)', '\g<pre>None\g<post>', line), # replace nil with None
	]
			
	result = []
	for line in lines:
		if line.startswith('//'):
			result.append('#'+line[2:])
			continue
		
		for f in filters:
			line = f(line)	

		result.extend(line.split('\n')) # in case a filter produced several lines
	return result

if __name__ == '__main__':	
	test_number = 1
	def test(foo, bar):
		global test_number
		if foo.strip() == bar.strip():
			print 'test %d successful' % test_number
		else:
			print 'test %d failed!' % test_number #' \n--- input ---\n%s\n--- expected result ---\n%s\n---' % (test_number, foo.strip(), bar.strip())
			import difflib
			for diff in difflib.ndiff(foo.split('\n'), bar.split('\n')):
				print diff
		test_number += 1
	
	test(objc_to_python("""pid_t pid=[[[[NSWorkspace sharedWorkspace]activeApplication]objectForKey:@"NSApplicationProcessIdentifier"]intValue];"""), "pid = NSWorkspace.sharedWorkspace().activeApplication().objectForKey_('NSApplicationProcessIdentifier').intValue()")

	test_source = """
		Fraction *frac = [[Fraction alloc] init];
	    Fraction *frac2 = [[Fraction alloc]init];
	    Fraction *frac3 = [[Fraction alloc] initWithNumerator: 3 denominator: 10];

	    // set the values
	    [frac setNumerator: 1];
	    [frac setDenominator: 3];
	"""
	expected_result = """
frac = Fraction.alloc().init()
frac2 = Fraction.alloc().init()
frac3 = Fraction.alloc().initWithNumerator_denominator_(3, 10)
# set the values
frac.setNumerator_(1)
frac.setDenominator_(3)"""
	test(objc_to_python(test_source), expected_result)

	test_source = """if(foo){bar(); Fraction* foo = [[Fraction alloc] init];} else {bar();} for (Foo* i in foos) {while(foo){asd()}}"""
	expected_result = """
if foo:
	bar()
	foo = Fraction.alloc().init()
else:
	bar()
for i in foos:
	while foo:
		asd()"""
	
	test(objc_to_python(test_source), expected_result)
	
	test(objc_to_python("""[NSThread detachNewThreadSelector:@selector(invokeService)
                             toTarget:self withObject:nil];
    """), 'NSThread.detachNewThreadSelector_toTarget_withObject_(invokeService, self, None)')
			
	test(objc_to_python('NSString* foo = @"foo";'), "foo = \'foo\'")
	test(objc_to_python('int foo = 2;'), "foo = 2")
	test(objc_to_python('- (unsigned int)countByEnumeratingWithState:(struct __objcFastEnumerationState *)state objects:(id *)items count:(unsigned int)stackcount;'), 'def countByEnumeratingWithState_objects_count_(self, state, items, stackcount)')
	
	test(objc_to_python("""
- (void)getSelection:(NSPasteboard *)pboard
	            userData:(NSString *)userData
	               error:(NSString **)error
{
    NSLog(@"Get Selection: %@ %d",userData,[userData characterAtIndex:0]);
    resultPboard=[pboard retain];
}
"""), """
def getSelection_userData_error_(self, pboard, userData, error):
	NSLog('Get Selection: %s %d',userData,userData.characterAtIndex_(0))
	resultPboard=pboard.retain()
""")

	objc_to_python("""
	#import "QSGlobalSelectionProvider.h"

	#define VERBOSE 1
	#define QSLog NSLog

	@implementation QSGlobalSelectionProvider

	NSTimeInterval failDate=0;

	- (void)registerProvider
	{
	    //[NSApp setServicesProvider:self];
	    //NSLog(@"Registered service provider");
	}

	- (void)getSelection:(NSPasteboard *)pboard
	            userData:(NSString *)userData
	               error:(NSString **)error
	{
	    NSLog(@"Get Selection: %@ %d",userData,[userData characterAtIndex:0]);
	    resultPboard=[pboard retain];
	}

	- (NSPasteboard *)getSelectionFromFrontApp
	{

	    //QSLog(@"GET SEL");
	    //id oldServicesProvider=[NSApp servicesProvider];
	    //[self invokeService];
	    [NSThread detachNewThreadSelector:@selector(invokeService)
	                             toTarget:self withObject:nil];

	    //      return nil;
	    NSRunLoop *loop=[NSRunLoop currentRunLoop];
	    NSDate *date=[NSDate date];
	    while(!resultPboard && [date timeIntervalSinceNow]>-2){
	        [loop runUntilDate:[NSDate dateWithTimeIntervalSinceNow:0.5]];
	    }
	    id result=[resultPboard autorelease];
	    resultPboard=nil;
	    return result;
	}


	- (void)dealloc
	{
	    QSLog(@"release");
	    [resultPboard release];
	    [super dealloc];
	}

	- (void)invokeService
	{
	    NSAutoreleasePool *pool=[[NSAutoreleasePool alloc]init];
	    pid_t pid=[[[[NSWorkspace sharedWorkspace]activeApplication]objectForKey:@"NSApplicationProcessIdentifier"]intValue];
	    AXUIElementRef app=AXUIElementCreateApplication (pid);

	    AXUIElementPostKeyboardEvent (app,(CGCharCode)0, (CGKeyCode)55, true ); //Command
	    AXUIElementPostKeyboardEvent (app,(CGCharCode)0, (CGKeyCode)53, true ); //Escape
	    AXUIElementPostKeyboardEvent (app,(CGCharCode)0, (CGKeyCode)53, false ); //Escape
	    AXUIElementPostKeyboardEvent (app,(CGCharCode)0, (CGKeyCode)55, true ); //Command
	    [pool release];
	}

	+(id)currentSelection{

	        NSPasteboard *pb=nil;

	        if ([NSDate timeIntervalSinceReferenceDate]-failDate > 3.0)
	            pb=[self getSelectionFromFrontApp];

	        if (!pb){
	            failDate=[NSDate timeIntervalSinceReferenceDate];
	            return nil;
	        }
	        return pb;
	}
	-(id)resolveProxyObject:(id)proxy{
	    id object=[QSGlobalSelectionProvider currentSelection];
	   return object;
	}
	-(BOOL)bypassValidation{
	    NSDictionary *appDictionary=[[NSWorkspace sharedWorkspace]activeApplication];
	    NSString *identifier=[appDictionary objectForKey:@"NSApplicationBundleIdentifier"];
	    if ([identifier isEqualToString:@"com.blacktree.Quicksilver"])
	        return YES;
	    else
	        return NO;
	}
	@end
""")
