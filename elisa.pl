out(Text):-write(Text).

in(Text):-
	nl,
	write("> "),
	readLine(Text).

readLine(Text):-
	get_char(Char),
	toLowerCase(Char,LChar),
	readLine2(LChar,Text).
readLine2('\n',[]):-!.
readLine2(LChar,[LChar|T]):-readLine(T).

charType('!', punctuation).
charType('?', punctuation).
charType('.', punctuation).
charType(',', punctuation).
charType(' ', whitespace).
charType('\t', whitespace).

toLowerCase(Char, LChar):-
	char_code(Char, Code),
	Code >= 'A',
	Code =< 'Z',
	NewCode is Code + 32,
	char_code(LChar, NewCode), !.
toLowerCase(Char, Char).

toUpperCase(Char, UChar):-
	char_code(Char, Code),
	Code >= 'a',
	Code =< 'z',
	NewCode is Code - 32,
	char_code(UChar, NewCode), !.
toUpperCase(Char, Char).

deleteChars([Char|Rest],Type,Out):-
	charType(Char, Type),
	deleteChars(Rest,Type,Out),!.
deleteChars([Char|Rest],Type,[Char|Out]):-
	deleteChars(Rest,Type,Out),!.
deleteChars([],_,[]).

toWords([],[]):-!.
toWords(Line, [Word|ResWords]):-
	readWord(Line, Word, ResLine),
	toWords(ResLine, ResWords).

readWord([], '', []).
readWord([Char|Res], '', Res) :- charType(Char, whitespace),!.
readWord([Char|ResLine], Word, Res) :-
	readWord(ResLine, ResWord, Res),
	atom_concat(Char, ResWord, Word).



:- dynamic resID/2.
resID(_,0).

% init:- inits the environment for simplification rules
init:-
	consult("simplification.pl"),
	consult("reply.pl").

simplify(In, Out):-
	deleteChars(In, punctuation, Out1),
	toWords(Out1,Out2),
	findSynonyms(Out2,Out3),
	Out = Out3.

findSynonyms(Words, Syn) :-
	sr(Words, Syn, RestWords, ResOutput),!,
	findSynonyms(RestWords, ResOutput).
findSynonyms([Word| ResWords], [Word| ResSyn]):-
	findSynonyms(ResWords, ResSyn),!.
findSynonyms([], []).

findReply(Words, Reply) :-
	findReply2(Words, -2, 0, [], ID, Reply),
	ID\=0,
	updateResID(ID).
findReply2([H|T], ActScore, _, _, ID, Res):-
	findall(Score,rules(_, Score,[H|T],_),Rules),
	Rules\=[],
	max_list(Rules,NewScore),
	ActScore<NewScore,
	rules(NewID, NewScore,[H|T],Replyes),
	resID(NewID,ResID),
	nth0(ResID,Replyes,NewReply),
	findReply2(T, NewScore, NewID, NewReply, ID, Res),!.
findReply2([_|T], ActScore, ActID, ActRes, ID, Res):-
	findReply2(T, ActScore, ActID, ActRes, ID, Res).
findReply2([], _, ID, Res, ID, Res).

updateResID(ID):-
	resID(ID,RID),
	once(rules(ID,_,_,Replyes)),
	length(Replyes, Len),
	NRID is (RID + 1) mod Len,
	retract((resID(ID,RID):-!)),
	asserta(resID(ID,NRID):-!),!.
updateResID(ID):-
	resID(ID,RID),
	once(rules(ID,_,_,Replyes)),
	length(Replyes, Len),
	NRID is (RID + 1) mod Len,
	asserta(resID(ID,NRID):-!).

writeWords([Word|Res]):-
	string_chars(Word,[Char|RChar]),
	toUpperCase(Char,UChar),
	readWord([UChar|RChar],Out,_),
	out(Out),
	writeWords2(Res).

writeWords2([Word|Res]):-
	is_list(Word),
	writeWords2(Word),
	writeWords2(Res),!.

writeWords2([Word|Res]):-
	charType(Word,punctuation),
	out(Word),
	writeWords2(Res),!.

writeWords2([Word|Res]):-
	out(" "),
	out(Word),
	writeWords2(Res),!.
writeWords2([]).

elisa:-out("Looking for Elisa....\n"),
       init,
       out("Here she is...\n\n"),
       out("Hello, I\'m Elisa, how can I help you?"),
       elisa([hi]).

elisa([quit|_]):-!.
elisa(_):-in(Line),
	  simplify(Line, Words),
	  findReply(Words,Reply),
	  writeWords(Reply),nl,
	  elisa(Words).






