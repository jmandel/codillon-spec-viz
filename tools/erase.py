import sys, re
def erase(src):
    out=[]
    for line in src.split('\n'):
        s=line.strip()
        if s.startswith('(@'):
            out.append(';; '+s); continue
        # erase (T | ...) refinements with paren matching
        res=''; i=0
        while i < len(line):
            m=re.match(r'\((i32|i64|f32|f64) \|', line[i:])
            if m:
                depth=0; j=i
                while True:
                    if line[j]=='(': depth+=1
                    elif line[j]==')':
                        depth-=1
                        if depth==0: break
                    j+=1
                res+=m.group(1); i=j+1
            else:
                res+=line[i]; i+=1
        out.append(res)
    return '\n'.join(out)
if __name__=='__main__':
    src=open(sys.argv[1]).read()
    body=erase(src)
    funcs=re.findall(r'\(func (\$\w+)', body)
    exports='\n'.join(f'(export "{f[1:]}" (func {f}))' for f in funcs)
    print('(module\n'+body+'\n'+exports+'\n)')
