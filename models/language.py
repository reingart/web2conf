if request.vars.force_language: session.language=request.vars.force_language
if session.language: T.force(session.language)
