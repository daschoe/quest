--reaper.ClearConsole()
reaper.ShowConsoleMsg("New try")
reaper.ShowConsoleMsg(reaper.GetPlayState())

if reaper.GetPlayState() == 0 then -- Stopped
  reaper.ShowConsoleMsg("\n")
  --reaper.ShowConsoleMsg(reaper.GetPlayPosition())
  reaper.ShowConsoleMsg("\n")
  reaper.ShowConsoleMsg( reaper.GetCursorPosition())
  reaper.ShowConsoleMsg("\n")
  proj, projfn = reaper.EnumProjects( -1 )
  markeridx, regionidx = reaper.GetLastMarkerAndCurRegion(proj, reaper.GetCursorPosition())
  --reaper.ShowConsoleMsg(markeridx)
  --reaper.ShowConsoleMsg("\n")
  retval, isrgn, pos, rgnend, name, markrgnindexnumber = reaper.EnumProjectMarkers(markeridx)
  --reaper.ShowConsoleMsg(retval)
  --reaper.ShowConsoleMsg(pos)
  if not (name == "!1016") and not (pos ==  reaper.GetCursorPosition()) then
    reaper.GoToMarker( proj, retval, true )
    reaper.ShowConsoleMsg("\n")
    reaper.ShowConsoleMsg(reaper.GetCursorPosition())
    reaper.OnPlayButton()
  end
  if pos ==  reaper.GetCursorPosition() then
    reaper.OnPlayButton()
  end
end
reaper.ShowConsoleMsg(reaper.GetPlayState())
