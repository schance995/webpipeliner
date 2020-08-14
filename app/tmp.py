def check_form_field(form, field, datatocompare, requires=None):
    if hasattr(form, field) and form[field].data:
        if (not requires) or form[requires].data:
            file = form[field].data
            data, err = read_data(file, datatocompare)        
            if err:
                for e in err:
                    flash(e, 'error')
            else:
                session['details'][field+'data'] = dumps(data)
        else:
            flash('Must upload both {}.tab and {}.tab'.format(field, requires), 'error')

if hasattr(form, 'groups') and form.groups.data:
            f = form.groups.data
            filename = secure_filename(f.filename) # to prevent cd ../ attacks, and gets the end filename
            # file must be converted from bytes to string
            groupsdata, err = read_groups(f.read().decode('utf-8').split('\n'), rawdata)
            if err:
                for e in err: flash(e, 'error')
            else:
                session['details']['groupsjson'] = dumps(groupsdata) # add the data for access later

        if hasattr(form, 'contrasts') and form.contrasts.data:
            if groupsdata:
                f = form.contrasts.data
                contrastsdata, err = read_contrasts(f.read().decode('utf-8').split('\n'), groupsdata['rgroups'])
                if err:
                    for e in err: flash(e, 'error')
                else:
                    session['details']['contrastsjson'] = dumps(contrastsdata)
            else:
                flash('Must also upload groups.tab in order to define contrasts.tab', 'error')

        if hasattr(form, 'peakcall') and form.peakcall.data:
            f = form.peakcall.data
            peaksdata, err = read_peaks(f.read().decode('utf-8').split('\n'), rawdata)
            if err:
                for e in err: flash(e, 'error')
            else:
                session['details']['peaksjson'] = dumps(peaksdata)

        if hasattr(form, 'pairs') and form.pairs.data:
            f = form.pairs.data
            pairsdata, err = read_pairs(f.read().decode('utf-8').split('\n'), rawdata)
            print(pairsdata, err)
            if err:
                for e in err: flash(e, 'error')
            else:
                session['details']['pairsjson'] = dumps(pairsdata)

        if hasattr(form, 'contrast') and form.contrast.data:
            if peaksdata:
                f = form.contrast.data
                groups_to_check = {row[-1] for row in peaksdata}
                contrast_data, err = read_contrast_(f.read().decode('utf-8').split('\n'), groups_to_check)
                if err:
                    for e in err:  flash(e, 'error')
                else:
                    session['details']['contrast_json'] = dumps(contrast_data)
        else:
            flash('Must also upload peakcall.tab to upload contrast.tab', 'error')